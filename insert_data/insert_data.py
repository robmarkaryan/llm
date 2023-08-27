from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from model import Company, Indicator, Stock, StockIndicator, Dividend
from datetime import date, datetime
import pandas as pd
from connection_str import DATABASE_URL

# Step 2: Create a SQLite in-memory database
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Step 3: Insert data
apple = Company(
    name='Apple Inc.',
    ticker_symbol='AAPL',
    industry='Technology',
    founded_date=date(1976, 4, 1)
)

microsoft = Company(
    name='Microsoft Corporation Common Stock',
    ticker_symbol='MSFT',
    industry='Technology',
    founded_date=date(1975, 4, 4)
)

# Add the instance to the session and commit to insert it into the database
session.add(apple)
session.commit()

session.add(microsoft)
session.commit()

# Step 3: Insert data
list_of_indicators = [
    Indicator(
        name='SMA_50',
        description='sma'
    ),
    Indicator(
        name='EMA_20',
        description='ema'
    ),
    Indicator(
        name='MACD_12_26_9',
        description='macd'
    ),
    Indicator(
        name='MACDh_12_26_9',
        description='macd h'
    ),
    Indicator(
        name='MACDs_12_26_9',
        description='macd s'
    ),
    Indicator(
        name='RSI_14',
        description='RSI_14'
    )
]

# Add the instance to the session and commit to insert it into the database
# for ind in list_of_indicators:
#     session.add(list_of_indicators)


[session.add(ind) for ind in list_of_indicators]
session.commit()

# Read CSV file
csv_file = 'stock_apple.csv'  # Provide the actual CSV file path
data = pd.read_csv(csv_file)

# Iterate through the rows of the CSV and insert data into the database
company = session.query(Company).filter_by(name='Apple Inc.').first()
for index, row in data.iterrows():
    stock = Stock(
        company=company,
        date=pd.to_datetime(row['Date']),
        open_price=float(row['Open'].replace('$', '')),
        close_price=float(row['Close/Last'].replace('$', '')),
        high_price=float(row['High'].replace('$', '')),
        low_price=float(row['Low'].replace('$', '')),
        volume=row['Volume'],  # Volume is already an integer
    )
    session.add(stock)

# Commit the changes
session.commit()

# Read CSV file
csv_file = 'stock_tesla.csv'  # Provide the actual CSV file path
data = pd.read_csv(csv_file)

# Iterate through the rows of the CSV and insert data into the database
company = session.query(Company).filter_by(name='Microsoft Corporation Common Stock').first()
for index, row in data.iterrows():
    stock = Stock(
        company=company,
        date=pd.to_datetime(row['Date']),
        open_price=float(row['Open'].replace('$', '')),
        close_price=float(row['Close/Last'].replace('$', '')),
        high_price=float(row['High'].replace('$', '')),
        low_price=float(row['Low'].replace('$', '')),
        volume=row['Volume'],  # Volume is already an integer
    )
    session.add(stock)

# Commit the changes
session.commit()


# Get all companies and indicators
stocks = session.query(Stock).all()
indicators = session.query(Indicator).all()

# Loop through each company and indicator combination
for stock in stocks:
    for indicator in indicators:
        # Create a new StockIndicator entry
        stock_indicator = StockIndicator(stock=stock, indicator=indicator)

        # Add the new entry to the session
        session.add(stock_indicator)

session.commit()


# Read the Excel file into a pandas DataFrame
df = pd.read_excel('divident_apple.xlsx', engine='openpyxl')
# Iterate through the Excel data and insert into Dividend table
for index, row in df.iterrows():
    company_id = row['Company id']

    # Find the corresponding company for the given company_id
    company = session.query(Company).filter_by(name='Apple Inc.').first()

    if company:
        dividend = Dividend(
            company=company,
            ex_dividend_date=row['Ex/EFF DATE'],
            pay_date=datetime.strptime(row['PAYMENT DATE'], '%m.%d.%Y').date() if isinstance(row['PAYMENT DATE'],
                                                                                             str) else row[
                'PAYMENT DATE'],
            amount=row['CASH AMOUNT'].replace('$', '')
        )
        session.add(dividend)


session.commit()
session.close()


# Read the Excel file into a pandas DataFrame
df = pd.read_excel('divident_tesla.xlsx', engine='openpyxl')
# Iterate through the Excel data and insert into Dividend table
for index, row in df.iterrows():
    company_id = row['Company id']

    # Find the corresponding company for the given company_id
    company = session.query(Company).filter_by(name='Microsoft Corporation Common Stock').first()

    if company:
        dividend = Dividend(
            company=company,
            ex_dividend_date=datetime.strptime(row['Ex/EFF DATE'], '%m.%d.%Y').date()
            if isinstance(row['Ex/EFF DATE'], str) else row['Ex/EFF DATE'],
            pay_date=datetime.strptime(row['PAYMENT DATE'], '%m.%d.%Y').date()
            if isinstance(row['PAYMENT DATE'], str) else row['PAYMENT DATE'],
            amount=row['CASH AMOUNT'].replace('$', '')
        )
        session.add(dividend)


session.commit()
session.close()
