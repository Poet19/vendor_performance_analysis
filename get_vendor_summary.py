# ===== IMPORTS & LOGGING SETUP =====
# ==========================================================
# Vendor Analytics Script
# This script creates a consolidated vendor performance
# dataset by combining purchase, sales and freight data.
#
# Steps:
# 1. Extract summary data from database
# 2. Clean and transform the dataset
# 3. Create analytical metrics
# 4. Load final dataset back to database
# ==========================================================

# Imports sqlite3 module for database connections and queries
import sqlite3
# Imports pandas for DataFrame operations and SQL execution
import pandas as pd
# Imports logging module for structured logging
import logging
# Imports os module for directory operations
import os
# Imports ingest_db function from etl_pipeline for data loading
from etl_pipeline import ingest_db



# ----------------------------------------------------------
# Create logs folder if not exists
# ----------------------------------------------------------
# Creates 'logs' directory if it doesn't exist (exist_ok=True prevents error if exists)
os.makedirs("logs", exist_ok=True)


# ----------------------------------------------------------
# SINGLE LOG FILE FOR ENTIRE PROJECT
# ----------------------------------------------------------
# Configures logging to single file for all project scripts with append mode and custom format
logging.basicConfig(
    filename="logs/project_pipeline.log",   # same log for all scripts
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",      # append mode (ETL + vendor summary same log)
    force=True         # prevents logging conflicts
)


# ==========================================================
# CREATE VENDOR SUMMARY DATASET
# ==========================================================

# ===== CREATE VENDOR SUMMARY FUNCTION =====
def create_vendor_summary(conn):

    # Logs start of vendor summary dataset creation
    logging.info("Creating vendor sales summary dataset")

    # Executes complex CTE query to create vendor_sales_summary DataFrame from database
    vendor_sales_summary = pd.read_sql_query("""

    -- ===============================================
    -- FreightSummary
    -- Calculate total freight cost per vendor
    -- ===============================================
    WITH FreightSummary AS (

        SELECT 
            VendorNumber,
            SUM(Freight) AS FreightCost

        FROM vendor_invoice

        GROUP BY VendorNumber
    ),

    -- ===============================================
    -- PurchaseSummary
    -- Aggregate vendor purchases by brand
    -- ===============================================
    PurchaseSummary AS (

        SELECT
            p.VendorNumber,
            p.VendorName,
            p.Brand,
            p.Description,

            -- average purchase price paid
            AVG(p.PurchasePrice) AS PurchasePrice,

            -- actual vendor price
            AVG(pp.Price) AS ActualPrice,

            -- product volume
            MAX(pp.Volume) AS Volume,

            -- total purchase quantity
            SUM(p.Quantity) AS TotalPurchaseQuantity,

            -- total purchase cost
            SUM(p.Dollars) AS TotalPurchaseDollars

        FROM purchases p

        JOIN purchase_prices pp
            ON p.Brand = pp.Brand

        WHERE p.PurchasePrice > 0

        GROUP BY
            p.VendorNumber,
            p.VendorName,
            p.Brand,
            p.Description
    ),

    -- ===============================================
    -- SalesSummary
    -- Aggregate sales performance per vendor & brand
    -- ===============================================
    SalesSummary AS (

        SELECT
            VendorNumber,
            Brand,

            SUM(SalesQuantity) AS TotalSalesQuantity,
            SUM(SalesDollars) AS TotalSalesDollars,
            SUM(SalesPrice) AS TotalSalesPrice,
            SUM(ExciseTax) AS TotalExciseTax

        FROM sales

        GROUP BY
            VendorNumber,
            Brand
    )


    -- ===============================================
    -- FINAL DATASET
    -- Combine purchase, sales and freight data
    -- ===============================================
    SELECT

        ps.VendorNumber,
        ps.VendorName,
        ps.Brand,
        ps.Description,

        ps.PurchasePrice,
        ps.ActualPrice,
        ps.Volume,

        ps.TotalPurchaseQuantity,
        ps.TotalPurchaseDollars,

        ss.TotalSalesQuantity,
        ss.TotalSalesDollars,
        ss.TotalSalesPrice,
        ss.TotalExciseTax,

        fs.FreightCost

    FROM PurchaseSummary ps

    LEFT JOIN SalesSummary ss
        ON ps.VendorNumber = ss.VendorNumber
        AND ps.Brand = ss.Brand

    LEFT JOIN FreightSummary fs
        ON ps.VendorNumber = fs.VendorNumber

    ORDER BY ps.TotalPurchaseDollars DESC

    """, conn)

    # Logs successful dataset creation
    logging.info("Vendor summary dataset created successfully")

    # Returns the created vendor_sales_summary DataFrame
    return vendor_sales_summary


# ==========================================================
# DATA CLEANING + FEATURE ENGINEERING
# ==========================================================

# ===== DATA CLEANING & FEATURE ENGINEERING FUNCTION =====
def clean_data(df):

    # Logs start of data cleaning process
    logging.info("Cleaning vendor dataset")

    # Converts 'Volume' column to numeric type, coercing errors to NaN
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')

    # Fills all NaN values in DataFrame with 0
    df.fillna(0, inplace=True)

    # Strips whitespace from VendorName column values
    df['VendorName'] = df['VendorName'].str.strip()
    # Strips whitespace from Description column values
    df['Description'] = df['Description'].str.strip()


    # ------------------------------------------------------
    # Feature Engineering (Analytical Metrics)
    # ------------------------------------------------------
    # ===== FEATURE ENGINEERING =====

    # Calculates Gross Profit column as TotalSalesDollars minus TotalPurchaseDollars
    df['GrossProfit'] = df['TotalSalesDollars'] - df['TotalPurchaseDollars']

    # Calculates ProfitMargin (%) safely avoiding division by zero (replace 0 sales with NaN)
    df['ProfitMargin'] = (
        df['GrossProfit'] /
        df['TotalSalesDollars'].replace(0, pd.NA)
    ) * 100

    # Calculates StockTurnover ratio safely avoiding division by zero
    df['StockTurnover'] = (
        df['TotalSalesQuantity'] /
        df['TotalPurchaseQuantity'].replace(0, pd.NA)
    )

    # Calculates SalesToPurchaseRatio safely avoiding division by zero
    df['SalesToPurchaseRatio'] = (
        df['TotalSalesDollars'] /
        df['TotalPurchaseDollars'].replace(0, pd.NA)
    )

    # Fills any remaining NaN values (from safe divisions) with 0
    df.fillna(0, inplace=True)

    # Logs successful completion of cleaning and feature engineering
    logging.info("Data cleaning completed")

    # Returns cleaned and enriched DataFrame
    return df


# ==========================================================
# MAIN EXECUTION BLOCK
# ==========================================================

# ===== MAIN EXECUTION BLOCK =====
if __name__ == "__main__":

    # Logs start of entire vendor summary pipeline
    logging.info("Starting vendor summary creation process")

    # Establishes SQLite connection to 'inventory.db'
    conn = sqlite3.connect('inventory.db')

    # Step 1: Calls function to create raw vendor summary dataset from CTE query
    vendor_summary = create_vendor_summary(conn)

    # Step 2: Applies cleaning, type conversion, and feature engineering
    cleaned_vendor_summary = clean_data(vendor_summary)

    # Step 3: Loads cleaned dataset to 'vendor_summary' table using ETL function
    ingest_db(cleaned_vendor_summary, 'vendor_summary', conn)

    # Closes database connection to free resources
    conn.close()

    # Logs successful pipeline completion
    logging.info("Vendor summary dataset created and loaded successfully")
    # Shuts down logging system cleanly
    logging.shutdown()
