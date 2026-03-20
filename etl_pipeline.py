# data ETL script – CSV files ko read karke SQL database me load karne ke liye
# This is a small data engineering task where CSV files are converted into SQL database tables.
# Table names are derived from CSV file names.
# If the same table already exists, it will be replaced with the new data.
# DataFrame index is not stored in the database.

import pandas as pd   
# pandas library import ki – CSV files read aur data handle karne ke liye

import os             
# os library import ki – folder ke andar files ko access karne ke liye

import logging
# logging library import ki – script ke execution ke dauran messages log karne ke liye

import time
# NEW: time module import kiya – script ko run hone me kitna time lagta hai measure karne ke liye

from sqlalchemy import create_engine   
# SQLAlchemy se create_engine function import kiya – database connection banane ke liye



# logging configuration
logging.basicConfig(
    filename="logs/etl_pipeline.log",   # logs folder ke andar log file create hogi
    level=logging.DEBUG,                # DEBUG level – sab detailed logs capture honge
    format="%(asctime)s - %(levelname)s - %(message)s",  # log format
    filemode="a"                        # append mode – purane logs delete nahi honge
)

engine = create_engine('sqlite:///inventory.db')  
# SQLite database create/connect ho raha hai
# agar inventory.db file exist nahi karti to Python automatically new database bana dega


def ingest_db(df, table_name, engine):
    # ye function dataframe ko SQL database me table ki form me load karta hai
    # df → pandas dataframe jisme CSV ka data hai
    # table_name → database table ka naam (CSV file name se derived)
    # engine → database connection object

    df.to_sql(
        table_name,      # table ka naam jo database me create hoga
        con=engine,      # database connection
        if_exists='append',   # NEW: replace ki jagah append use kar rahe hain
        # WHY: jab hum chunks me data load karenge to har batch database me add hoga
        # agar replace use karte to har chunk previous data ko overwrite kar deta

        index=False,      # dataframe ka index column database me store nahi hoga
        chunksize=50000   # NEW: data ko batches me database me insert karega
        # WHY: large datasets (millions of rows) ek hi baar insert karne se memory crash ho sakti hai
        # chunksize=50000 ka matlab hai 50k rows ek time me database me jayengi
    )


# NEW: loop ko ek function ke andar daal diya gaya hai taaki code modular aur reusable ho
def load_raw_data():
    start = time.time()
    # NEW: script start hone ka time record kar rahe hain
    logging.info("Starting data ingestion") 

    for file in os.listdir('data'):
        # data folder ki sab files loop me read ho rahi hain

        if '.csv' in file:
            # sirf csv files process karni hain

            logging.info(f"Ingesting {file} into database")
            # logging message taaki pata chale kaunsi file database me load ho rahi hai


            # NEW: CSV ko chunks me read kar rahe hain
            # WHY: agar file bahut badi ho (jaise sales.csv with 12M rows) to memory error ho sakta hai
            # chunksize use karne se CSV bhi batches me read hoti hai

            for i, chunk in enumerate(pd.read_csv('data/' + file, chunksize=50000), start=1):

                logging.info(f"Processing chunk {i}")
                # chunk number log ho raha hai taaki pata chale kitne batches process ho rahe hain


                df = chunk
                # CSV chunk ko dataframe ki tarah treat kar rahe hain


                print("Shape:", df.shape)
                # dataframe ka size batata hai (rows, columns)


                logging.debug(f"Shape of {file}: {df.shape}")
                # dataframe shape log file me store ho rahi hai


                #ingest_db(df, file[:-4], engine) this is string slicing to remove last 4 characters from file name (which is .csv) to get the table name for database
                # file[:-4] → CSV file name se last 4 characters (.csv) remove karke
                # usko database table name bana rahe hain


                ingest_db(df, file.replace('.csv',''), engine)
                # ingest_db function ko call kar rahe hain
                # CSV file ka naam table name ban raha hai (.csv remove karke)


            print(file, "loaded into database")
            # confirm karne ke liye message print ho raha hai ki data database me load ho gaya


    end = time.time()
    # NEW: script end hone ka time record

    total_time = (end - start) / 60
    # NEW: total execution time calculate kar rahe hain minutes me

    logging.info(f"Total ingestion time: {total_time:.2f} minutes")
    # NEW: log file me total execution time record ho raha hai

    logging.info("Ingestion Complete")
    # NEW: final completion message


# NEW: function call kar rahe hain taaki ETL process run ho
load_raw_data()
print("ETL started")


# Python scripting matlab:
# Python me ek automated program likhna jo repetitive kaam automatically kare

# Data ingestion ka matlab:
# data ko source system se destination system me load karna
# yahan source = CSV files
# destination = SQLite database tables

#when there is a big data set read all the data using excel and using sql quereis onoy load the required data into the database. This is a common practice in data engineering to optimize performance and storage.

