# ===== IMPORTS & DATABASE SETUP =====
# Understanding the dataset to explore how the data is structured in the database 
# and to determine whether creating aggregate tables could support vendor selection, 
# profitability analysis, and product pricing optimization.

# Imports pandas library for data manipulation and analysis using DataFrames
import pandas as pd
# Imports sqlite3 module for connecting to and querying SQLite databases
import sqlite3

# Creates a connection object to the SQLite database file 'inventory.db' for executing SQL queries
conn = sqlite3.connect('inventory.db')


# -------------------------------------------------------
# 1️⃣ Check tables in database
# -------------------------------------------------------
# ===== DATABASE EXPLORATION: LIST TABLES =====

# Executes SQL query to retrieve all table names from SQLite metadata and loads into DataFrame
tables = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table';", conn
)

# Prints header message indicating table list output
print("Tables in the database:")
# Prints the DataFrame containing table names
print(tables)


# -------------------------------------------------------
# 2️⃣ Preview structure of each table
# -------------------------------------------------------

for table in tables['name']:

    print("-"*50, table, "-"*50)

    row_count = pd.read_sql_query(
        f"SELECT COUNT(*) AS count FROM {table}", conn
    )['count'].values[0]

    print("Count of records:", row_count)

    print(f"\nFirst 5 records from {table} table:")

    query = f"SELECT * FROM {table} LIMIT 5"
    df = pd.read_sql_query(query, conn)

    print(df)


# -------------------------------------------------------
# 3️⃣ Vendor level filtering (Vendor 4466)
# -------------------------------------------------------

# lets filter out a unique vendor from the list and all the information around it

purchases = pd.read_sql_query(
    "SELECT * FROM purchases WHERE VendorNumber = 4466", conn
)

purchase_prices = pd.read_sql_query(
    "SELECT * FROM purchase_prices WHERE VendorNumber = 4466", conn
)

vendor_invoice = pd.read_sql_query(
    "SELECT * FROM vendor_invoice WHERE VendorNumber = 4466", conn
)

sales = pd.read_sql_query(
    "SELECT * FROM sales WHERE VendorNumber = 4466", conn
)


print(purchases)
print(purchase_prices)
print(vendor_invoice)
print(sales)


# -------------------------------------------------------
# 4️⃣ Purchase analysis
# -------------------------------------------------------

# kaunsa brand kis price par kitni quantity me purchase hua 
# aur uspe total kitna paisa spend hua.

print(
    purchases
    .groupby(['Brand','PurchasePrice'])[['Quantity','Dollars']]
    .sum()
)


# -------------------------------------------------------
# 5️⃣ Vendor invoice validation
# -------------------------------------------------------

print(vendor_invoice.columns)

# This line of code prints the column names of the 'vendor_invoice' DataFrame.

print(vendor_invoice['PONumber'].nunique())
print(vendor_invoice.shape[0])

# both the values are same which means there are no duplicate PONumbers in the vendor_invoice table. 
# Each PONumber is unique, indicating that each purchase order is distinct and there are no repeated entries.


# -------------------------------------------------------
# 6️⃣ Sales performance analysis
# -------------------------------------------------------
# ===== SALES PERFORMANCE ANALYSIS =====

# Groups 'sales' DataFrame by 'Brand', sums 'SalesDollars', 'SalesPrice', 'SalesQuantity'; prints result
print(
    sales
    .groupby('Brand')[['SalesDollars','SalesPrice','SalesQuantity']]
    .sum()
)

# groupby('Brand') → sales data ko Brand ke basis par groups me divide karta hai
# [['SalesDollars','SalesPrice','SalesQuantity']] → analysis ke liye sirf ye 3 columns select karta hai
# sum() → har Brand group ke liye in columns ka total calculate karta hai
# Har brand ke liye total sales quantity aur total sales revenue nikalna taaki pata chale 
# kaunsa brand sabse zyada perform kar raha hai.



#insights

# The purchases table contains actual purchase data, including the date of purchase, products (brands) purchased by vendors, the amount paid (in dollars), and the quantity purchased.
# The purchase price column is derived from the purchase_prices table, which provides product-wise actual and purchase prices. The combination of vendor and brand is unique in this table.
# The vendor_invoice table aggregates data from the purchases table, summarizing quantity and dollar amounts, along with an additional column for freight. This table maintains uniqueness based on vendor and PO number.
# The sales table captures actual sales transactions, detailing the brands purchased by vendors, the quantity sold, the selling price, and the revenue earned.


##As the data that we need for analysis is distributed in different tables, we need to create a summary table containing:
# purchase transactions made by vendors
# sales transaction data
# freight costs for each vendor
# actual product prices from vendors


# ===== PRE-QUERY SUMMARY AGGREGATIONS =====
# Prints vendor_invoice columns (duplicate print from earlier validation)
print (vendor_invoice.columns)

# Queries and computes total FreightCost summed by VendorNumber from vendor_invoice table
freight_summary = (pd.read_sql_query("""select VendorNumber, sum(Freight) as FreightCost from vendor_invoice group by VendorNumber""", conn))
# Prints the freight_summary DataFrame
print (freight_summary)

# Queries joined purchases and purchase_prices, aggregates TotalPurchaseQuantity and TotalPurchaseDollars by VendorNumber, VendorName, Brand; prints result
print(pd.read_sql_query("""select p.VendorNumber, p.VendorName, p.Brand, p.PurchasePrice, pp.Volume , pp.Price as ActualPrice, 
                        sum(p.Quantity) as TotalPurchaseQuantity, 
                        sum(p.Dollars) as TotalPurchaseDollars from purchases p join purchase_prices pp on p.Brand = pp.Brand where p.PurchasePrice >0 group by  p.VendorNumber, p.VendorName, p.Brand order by TotalPurchaseDollars """, conn))

# Prints sales DataFrame columns
print(sales.columns)
# Queries sales table, aggregates sales metrics by VendorNumber and Brand; prints result
print(pd.read_sql_query("""select VendorNumber, Brand, 
                        sum(SalesQuantity) as TotalSalesQuantity, 
                        sum(SalesPrice) as TotalSalesPrice, 
                        sum(SalesDollars) as TotalSalesDollars, sum(ExciseTax) as TotalExciseTax from sales group by VendorNumber, Brand order by TotalSalesDollars""", conn))

# Imports time module for measuring query execution time
import time

# ===== PERFORMANCE TIMING & SLOWER APPROACH (COMMENTED OUT) =====
# Records start time for measuring query execution duration
start = time.time()

# ========================================
# SLOWER APPROACH (DIRECT BIG JOIN) - COMMENTED OUT
# ========================================
# This direct multi-table JOIN without pre-aggregation is slower for large datasets
# because it performs aggregations (SUM) on full joined tables every time
# final_table = pd.read_sql_query("""
# SELECT 
#     pp.VendorNumber,
#     pp.Brand,
#     pp.Price AS ActualPrice,
#     pp.PurchasePrice,

#     SUM(s.SalesQuantity) AS TotalSalesQuantity,
#     SUM(s.SalesDollars) AS TotalSalesDollars,
#     SUM(s.SalesPrice) AS TotalSalesPrice,
#     SUM(s.ExciseTax) AS TotalExciseTax,

#     SUM(vi.Quantity) AS TotalPurchaseQuantity,
#     SUM(vi.Dollars) AS TotalPurchaseDollars,
#     SUM(vi.Freight) AS TotalFreightCost

# FROM purchase_prices pp

# JOIN sales s
# ON pp.VendorNumber = s.VendorNumber
# AND pp.Brand = s.Brand

# JOIN vendor_invoice vi
# ON pp.VendorNumber = vi.VendorNumber

# GROUP BY 
# pp.VendorNumber,
# pp.Brand,
# pp.Price,
# pp.PurchasePrice
# """, conn)

# print(final_table)


# ==============================
# DATA ARCHITECTURE OVERVIEW
# ==============================

# The dataset is distributed across multiple relational tables:

# purchases
# → contains actual purchase transactions such as:
#   VendorNumber, Brand, PurchasePrice, Quantity purchased, and Dollars spent.

# purchase_prices
# → contains the official vendor price list for products including:
#   actual product price and product volume.

# sales
# → contains actual sales transactions such as:
#   sales quantity, revenue generated, selling price, and excise tax.

# vendor_invoice
# → contains aggregated vendor invoice information including:
#   total purchase amount and freight cost charged by vendors.


# Since the information required for vendor performance analysis
# is distributed across different tables, we first create intermediate
# summary tables using SQL aggregations (CTEs).


# FreightSummary
# → calculates total freight cost incurred for each vendor.

# PurchaseSummary
# → summarizes purchase activity per vendor and brand including:
#   total quantity purchased and total dollars spent.

# SalesSummary
# → summarizes sales activity per vendor and brand including:
#   total quantity sold and total sales revenue.


# These intermediate summary tables are then joined together to build
# a final analytical dataset called "vendor_sales_summary".

# This dataset contains vendor information, brand details,
# purchase cost, sales revenue, and freight cost, which can be used
# for vendor performance analysis and profitability evaluation.


# ======================================
# BUILDING FINAL ANALYTICAL DATASET
# ======================================
vendor_sales_summary = pd.read_sql_query("""

-- ==============================
-- FREIGHT SUMMARY
-- ==============================
-- Calculate total freight cost paid to each vendor

WITH FreightSummary AS (

    SELECT
        VendorNumber,
        SUM(Freight) AS FreightCost

    FROM vendor_invoice

    GROUP BY VendorNumber
),

-- ==============================
-- PURCHASE SUMMARY
-- ==============================
-- Aggregate purchase transactions per Vendor + Brand

PurchaseSummary AS (

    SELECT
        p.VendorNumber,
        p.VendorName,
        p.Brand,
        p.Description,

        -- average price vendor paid
        AVG(p.PurchasePrice) AS PurchasePrice,

        -- actual vendor catalog price
        AVG(pp.Price) AS ActualPrice,

        -- product volume
        MAX(pp.Volume) AS Volume,

        -- total quantity purchased
        SUM(p.Quantity) AS TotalPurchaseQuantity,

        -- total money spent
        SUM(p.Dollars) AS TotalPurchaseDollars

    FROM purchases p

    INNER JOIN purchase_prices pp
        ON p.Brand = pp.Brand

    WHERE p.PurchasePrice > 0

    GROUP BY
        p.VendorNumber,
        p.VendorName,
        p.Brand,
        p.Description
),

-- ==============================
-- SALES SUMMARY
-- ==============================
-- Aggregate sales transactions per Vendor + Brand

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

-- ==============================
-- FINAL ANALYTICAL DATASET
-- ==============================

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


print(vendor_sales_summary)


# ==============================
# PERFORMANCE OPTIMIZATION
# ==============================

# This query aggregates large transactional tables (purchases, sales)
# into intermediate summary tables using CTEs.

# Pre-aggregating the data reduces expensive computations when performing
# analytics or building dashboards.

# The final table `vendor_sales_summary` acts as an analytical dataset
# that combines purchase, sales, and freight information.

# This structure improves performance for reporting, vendor comparison,
# profitability analysis, and dashboard visualization.


end = time.time()

print("Time taken to execute the query:", end - start, "seconds")

# ===== DATA QUALITY CHECKS & CLEANING =====
# Prints data types of all columns in vendor_sales_summary DataFrame
print(vendor_sales_summary.dtypes)
# Counts null values in each column of vendor_sales_summary
print(vendor_sales_summary.isnull().sum())
# Displays first 5 rows of vendor_sales_summary for inspection
print(vendor_sales_summary.head())
# Prints summary statistics (count, mean, std, min, max, quartiles) for numeric columns
print(vendor_sales_summary.describe())
# Prints unique VendorName values to identify whitespace issues
print(vendor_sales_summary['VendorName'].unique()) #irreoevanlt white spaces in vendor names
# Prints unique Description values for inspection
print(vendor_sales_summary['Description'].unique()) 

#3 inconsistency fosrt is voolume data tyoe then there are some null values in the dataset and then there are some irrelevant white spaces in the vendor names which we need to clean before doing any analysis.

# Converts 'Volume' column to float data type to fix type inconsistency
vendor_sales_summary['Volume'] = vendor_sales_summary['Volume'].astype(float)

# Replaces all null (NaN) values in the DataFrame with 0
vendor_sales_summary.fillna(0, inplace=True)

# Removes leading/trailing whitespace from all values in 'VendorName' column
vendor_sales_summary['VendorName'] = vendor_sales_summary['VendorName'].str.strip()

# Re-prints data types after cleaning
print(vendor_sales_summary.dtypes)
# Re-prints null counts after cleaning (should be 0)
print(vendor_sales_summary.isnull().sum())
# Re-prints first 5 rows after cleaning
print(vendor_sales_summary.head())
# Re-prints summary statistics after cleaning
print(vendor_sales_summary.describe())
# Re-prints unique VendorName values after stripping whitespace
print(vendor_sales_summary['VendorName'].unique())
# Re-prints unique Description values after cleaning
print(vendor_sales_summary['Description'].unique())


# ===== PROFITABILITY & PERFORMANCE METRICS =====
#creating new columns for profitability analysis and vendor selection

# Calculates GrossProfit as TotalSalesDollars minus TotalPurchaseDollars for each row
vendor_sales_summary['GrossProfit'] = vendor_sales_summary['TotalSalesDollars'] - vendor_sales_summary['TotalPurchaseDollars']
# Prints GrossProfit column
print(vendor_sales_summary[['GrossProfit']])
# Prints minimum GrossProfit value across all rows
print(vendor_sales_summary['GrossProfit'].min())

# Calculates ProfitMargin as (GrossProfit / TotalSalesDollars) * 100 percentage
vendor_sales_summary['ProfitMargin'] = vendor_sales_summary['GrossProfit'] / vendor_sales_summary['TotalSalesDollars']*100
# Prints ProfitMargin column
print(vendor_sales_summary[['ProfitMargin']])

# Calculates StockTurnover ratio as TotalSalesQuantity divided by TotalPurchaseQuantity
vendor_sales_summary['StockTurnover'] = vendor_sales_summary['TotalSalesQuantity'] / vendor_sales_summary['TotalPurchaseQuantity']
# Prints StockTurnover column
print(vendor_sales_summary[['StockTurnover']])

# Calculates SalesToPurchaseRatio as TotalSalesDollars divided by TotalPurchaseDollars
vendor_sales_summary['SalestoPurchaseRatio'] = vendor_sales_summary['TotalSalesDollars'] / vendor_sales_summary['TotalPurchaseDollars']
# Prints SalestoPurchaseRatio column
print(vendor_sales_summary[['SalestoPurchaseRatio']])

# ===== SAVE SUMMARY TABLE TO DATABASE =====
#lest create new table and save it to the database for future analysis and dashboarding

# Creates SQLite cursor object for executing DDL statements
cursor = conn.cursor()

# Drops existing vendor_sales_summary table if it exists to avoid conflicts
cursor.execute("DROP TABLE IF EXISTS vendor_sales_summary")

# Creates new vendor_sales_summary table with all columns including new metrics and primary key constraint
cursor.execute("""
CREATE TABLE vendor_sales_summary (
    VendorNumber INT,
    VendorName TEXT,
    Brand INT,
    Description TEXT,
    PurchasePrice REAL,
    ActualPrice REAL,
    Volume REAL,
    TotalPurchaseQuantity INT,
    TotalPurchaseDollars REAL,
    TotalSalesQuantity INT,
    TotalSalesDollars REAL,
    TotalSalesPrice REAL,
    TotalExciseTax REAL,
    FreightCost REAL,
    GrossProfit REAL,
    ProfitMargin REAL,
    StockTurnover REAL,
    SalesToPurchaseRatio REAL,
    PRIMARY KEY (VendorNumber, Brand)
)
""")

# Commits the CREATE TABLE transaction to database
conn.commit()

# Inserts cleaned vendor_sales_summary DataFrame into the new table (append mode)
vendor_sales_summary.to_sql(
    'vendor_sales_summary',
    conn,
    if_exists='append',
    index=False
)

# Queries and prints first 5 rows from the saved vendor_sales_summary table to verify
print(pd.read_sql_query(
    "SELECT * FROM vendor_sales_summary LIMIT 5",
    conn
))
