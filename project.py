import requests
import pandas as pd
import numpy as np
import logging
import matplotlib.pyplot as plt
from fpdf import FPDF

class CurrencyDataAnalyzer:
    def __init__(self, api_key, from_currency, to_currency):
        self.api_key = api_key
        self.from_currency = from_currency
        self.to_currency = to_currency
        self.data = None
        self.analysis = None
        self.signals = None

    def fetch_currency_data(self):
        logging.info(f"Fetching data for {self.from_currency}{self.to_currency}")
        url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={self.from_currency}&to_symbol={self.to_currency}&apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError("Failed to fetch data from Alpha Vantage.")
        self.data = response.json()
    
    def preprocess_data(self, data):
        logging.info("Preprocessing data")
        df = pd.DataFrame.from_dict(data, orient='index', dtype=float)
        df = df.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close'
        })
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        return df
    
    def calculate_rsi(self, data, window=14):
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze_currency_strength(self):
        logging.info("Analyzing currency strength")
        df = self.preprocess_data(self.data['Time Series FX (Daily)'])
        df['RSI'] = self.calculate_rsi(df['Close'])
        self.analysis = df
    
    def generate_trade_signals(self):
        logging.info("Generating trade signals")
        df = self.analysis.copy()
        df.loc[df['RSI'] > 70, 'Signal'] = -1  # Sell signal
        df.loc[df['RSI'] < 30, 'Signal'] = 1   # Buy signal
        df['Signal'] = df['Signal'].fillna(0)
        df['Position'] = df['Signal'].shift()
        self.signals = df

    def plot_data(self):
        logging.info("Plotting data")
        plt.figure(figsize=(14, 7))

        plt.subplot(2, 1, 1)
        plt.plot(self.analysis['Close'], label='Close Price')
        plt.title('Currency Close Price')
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(self.analysis['RSI'], label='RSI', color='orange')
        plt.axhline(70, color='red', linestyle='--')
        plt.axhline(30, color='green', linestyle='--')
        plt.title('RSI')
        plt.legend()

        buy_signals = self.signals[self.signals['Signal'] == 1]
        sell_signals = self.signals[self.signals['Signal'] == -1]

        plt.scatter(buy_signals.index, self.analysis.loc[buy_signals.index]['Close'], marker='^', color='green', label='Buy Signal')
        plt.scatter(sell_signals.index, self.analysis.loc[sell_signals.index]['Close'], marker='v', color='red', label='Sell Signal')

        plt.legend()
        plt.tight_layout()
        plt.savefig('currency_analysis.png')

    def generate_report(self):
        logging.info("Generating PDF report")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Currency Data Analysis Report", ln=True, align='C')
        pdf.image('currency_analysis.png', x=10, y=20, w=190)
        pdf.output("report.pdf")

def main():
    api_key = "XEJ20Z4TH12XU4HQ"
    from_currency = "EUR"
    to_currency = "USD"
    analyzer = CurrencyDataAnalyzer(api_key, from_currency, to_currency)
    analyzer.fetch_currency_data()
    analyzer.analyze_currency_strength()
    analyzer.generate_trade_signals()
    analyzer.plot_data()
    analyzer.generate_report()

if __name__ == "__main__":
    main()









