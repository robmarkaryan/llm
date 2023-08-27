from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from connection_str import DATABASE_URL

# Replace 'your_database_uri' with the actual URI of your PostgreSQL database
engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ticker_symbol = Column(String, unique=True)
    industry = Column(String)
    founded_date = Column(Date)

    stocks = relationship('Stock', back_populates='company')
    dividends = relationship('Dividend', back_populates='company')  # Corrected relationship definition


class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    date = Column(Date)
    open_price = Column(Float)
    close_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    volume = Column(Integer)

    company = relationship('Company', back_populates='stocks')
    indicators = relationship('StockIndicator', back_populates='stock')  # Added for clarity


class Indicator(Base):
    __tablename__ = 'indicators'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    stocks = relationship('StockIndicator', back_populates='indicator')  # Added for clarity


class StockIndicator(Base):
    __tablename__ = 'stock_indicators'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    indicator_id = Column(Integer, ForeignKey('indicators.id'))

    stock = relationship('Stock', back_populates='indicators')
    indicator = relationship('Indicator', back_populates='stocks')


class Dividend(Base):
    __tablename__ = 'dividends'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    ex_dividend_date = Column(Date)
    pay_date = Column(Date)
    amount = Column(Float)

    company = relationship('Company', back_populates='dividends')  # Corrected relationship definition


# Create the tables in the database
Base.metadata.create_all(engine)
