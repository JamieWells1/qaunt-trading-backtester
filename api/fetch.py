import json
import yfinance as yf
import logging


# AAPL, "15m", "2024-12-11", "2024-12-18"
def get_df_selected_tf(
    ticker, _interval, _start_date, _end_date
):  # For a selected timeframe
    data = yf.download(
        ticker, interval=_interval, start=_start_date, end=_end_date, progress=False
    )
    if ("Adj Close", ticker) in data.columns:
        data = data.drop(columns=[("Adj Close", ticker)])

    return data, ticker


# AAPL, "15m", "5d"
def get_df_recent(ticker, _interval, _period):  # For the most recent timeframe
    data = yf.download(ticker, interval=_interval, period=_period, progress=False)
    if ("Adj Close", ticker) in data.columns:
        data = data.drop(columns=[("Adj Close", ticker)])

    return data, ticker


# Get settings from config.json
def get_settings():
    with open("config.json", "r") as settings:
        return json.load(settings)
