import tkinter as tk
from tkinter import ttk
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import StockIndicator, Stock, Indicator, Company, Dividend  # Import your database models
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import pandas_ta as ta
from connection_str import DATABASE_URL

# Create a connection to the PostgreSQL database
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class StockViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Viewer")

        self.stock_combo = ttk.Combobox(self.root)
        self.stock_combo.grid(row=0, column=0, padx=10, pady=10)
        self.update_stock_combo()

        self.plot_button = tk.Button(self.root, text="Plot", command=self.plot_data)
        self.plot_button.grid(row=0, column=1, padx=10, pady=10)

        self.indicator_combo = ttk.Combobox(self.root)
        self.indicator_combo.grid(row=0, column=2, padx=10, pady=10)

        self.plot_button = tk.Button(self.root, text="Plot Indicator", command=self.plot_indicator)
        self.plot_button.grid(row=0, column=3, padx=10, pady=10)
        self.update_indicator_combo()

        self.dividend_button = tk.Button(self.root, text="Plot Dividends", command=self.plot_dividends)
        self.dividend_button.grid(row=0, column=4, padx=10, pady=10)

        self.canvas = None

    def update_stock_combo(self):
        companies = session.query(Company).all()
        company_names = [company.name for company in companies]
        self.stock_combo["values"] = company_names

    def update_indicator_combo(self):
        indicators = session.query(Indicator).all()
        indicator_names = [indicator.name for indicator in indicators]
        self.indicator_combo["values"] = indicator_names

    def plot_data(self):
        selected_company_name = self.stock_combo.get()

        # Get the company ID based on the selected company name
        selected_company = session.query(Company).filter_by(name=selected_company_name).first()
        if selected_company is None:
            return

        # Fetch all relevant stock data for the selected company ID
        stock_data = session.query(Stock).filter_by(company_id=selected_company.id).all()

        df = pd.DataFrame(
            [(s.date, s.open_price, s.close_price, s.high_price, s.low_price, s.volume) for s in stock_data])
        df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(df['date'], df['close'], label='close price')
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.set_title("Stock Data")
        ax.legend()
        plt.xticks(rotation=45)

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=1, columnspan=5, padx=10, pady=10)

    def plot_indicator(self):
        selected_company_name = self.stock_combo.get()
        selected_indicator_name = self.indicator_combo.get()

        # Get the company ID based on the selected company name
        selected_company = session.query(Company).filter_by(name=selected_company_name).first()
        if selected_company is None:
            return

        # Get the selected indicator based on the selected indicator name
        selected_indicator = session.query(Indicator).filter_by(name=selected_indicator_name).first()
        if selected_indicator is None:
            return

        # Fetch all relevant stock data for the selected company ID
        stock_data = session.query(Stock).filter_by(company_id=selected_company.id).all()

        df = pd.DataFrame(
            [(s.date, s.open_price, s.close_price, s.high_price, s.low_price, s.volume) for s in stock_data])
        df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']

        # Add technical analysis indicators using pandas_ta
        df.ta.sma(length=50, append=True)
        df.ta.ema(length=20, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.bbands(length=20, std=2, append=True)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(df['date'], df['close'], label='close price')
        ax.plot(df['date'], df[selected_indicator.name], label=df[selected_indicator.name].name)
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.set_title("Stock Data with Indicators")
        ax.legend()
        plt.xticks(rotation=45)

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=1, columnspan=5, padx=10, pady=10)

    def plot_dividends(self):


        selected_company_name = self.stock_combo.get()

        # Get the company ID based on the selected company name
        selected_company = session.query(Company).filter_by(name=selected_company_name).first()
        if selected_company is None:
            return

        # Fetch all relevant dividend data for the selected company ID
        dividend_data = session.query(Dividend).filter_by(company_id=selected_company.id).order_by(
            Dividend.ex_dividend_date).all()

        dividend_df = pd.DataFrame(
            [(d.ex_dividend_date, d.pay_date, d.amount) for d in dividend_data])
        dividend_df.columns = ['ex_dividend_date', 'pay_date', 'amount']

        new_window = tk.Toplevel(self.root)
        new_window.title("Dividend Viewer")
        new_window.geometry("1200x600")  # Set your desired dimensions

        self.save_button = tk.Button(new_window, text="Save Changes", command=self.save_changes)
        self.save_button.pack(pady=10)
        self.save_button.config(command=self.save_changes)

        self.dividend_table = ttk.Treeview(new_window, show='headings',
                                           columns=("ex_dividend_date", "pay_date", "amount"), selectmode="browse")

        self.dividend_table = ttk.Treeview(new_window)
        self.dividend_table["columns"] = ("company_name", "ex_dividend_date", "pay_date", "amount")
        self.dividend_table.heading("company_name", text="Company Name")
        self.dividend_table.heading("ex_dividend_date", text="Ex-Dividend Date")
        self.dividend_table.heading("pay_date", text="Pay Date")
        self.dividend_table.heading("amount", text="Amount")

        self.dividend_table.column("company_name", anchor="center")
        self.dividend_table.column("ex_dividend_date", anchor="center")
        self.dividend_table.column("pay_date", anchor="center")
        self.dividend_table.column("amount", anchor="center")

        # Enable editing
        self.dividend_table.bind('<Double-1>', self.on_item_double_click)

        vsb = ttk.Scrollbar(new_window, orient="vertical", command=self.dividend_table.yview)
        vsb.pack(side='right', fill='y')
        self.dividend_table.configure(yscrollcommand=vsb.set)

        self.dividend_table.pack(fill="both", expand=True)

        for index, row in dividend_df.iterrows():
            company_name = session.query(Company).get(selected_company.id).name
            self.dividend_table.insert("", "end",
                                       values=(company_name, row['ex_dividend_date'], row['pay_date'], row['amount']))

    def on_item_double_click(self, event):
        item_id = self.dividend_table.focus()
        column = self.dividend_table.identify_column(event.x)

        if item_id and column:
            item_index = self.dividend_table.index(item_id)
            col_idx = int(column.lstrip('#')) - 1

            # Ensure the first column is editable
            self.edit_entry = tk.Entry(self.dividend_table, validate="key")
            self.edit_entry.bind("<Return>", lambda event, item_id=item_id, col_idx=col_idx: self.update_edited_cell(event, item_id, col_idx))
            self.edit_entry.bind("<FocusOut>", lambda event, item_id=item_id, col_idx=col_idx: self.update_edited_cell(event, item_id, col_idx))
            self.edit_entry.grid(row=item_index, column=col_idx, sticky="nsew")
            self.edit_entry.insert(0, self.dividend_table.item(item_id, "values")[col_idx])
            self.edit_entry.focus_set()

    def update_edited_cell(self, event, item_id, col_idx):
        new_value = self.edit_entry.get()
        self.dividend_table.set(item_id, col_idx, new_value)
        self.edit_entry.destroy()

    def save_changes(self):
        selected_item_id = self.dividend_table.focus()
        if selected_item_id:
            selected_item_values = self.dividend_table.item(selected_item_id, "values")
            selected_company_name = selected_item_values[0]
            ex_dividend_date = selected_item_values[1]
            pay_date = selected_item_values[2]
            new_amount = selected_item_values[3]

            selected_company = session.query(Company).filter_by(name=selected_company_name).first()
            selected_dividend = session.query(Dividend).filter_by(company_id=selected_company.id,
                                                                  ex_dividend_date=ex_dividend_date,
                                                                  pay_date=pay_date).first()

            if selected_dividend:
                selected_dividend.amount = new_amount
                session.commit()


if __name__ == "__main__":
    root = tk.Tk()
    app = StockViewerApp(root)
    root.mainloop()
