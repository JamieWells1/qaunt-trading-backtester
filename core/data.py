import api.GraphData as api
import api.fetch as fetch
import core.order as order
import utils.variables as utils
import os
import pandas as pd


def init_graph_data(account):
    config = fetch.get_settings()

    if not config["general"]["dummyData"]:
        if not config["general"]["mostRecent"]:
            df, ticker = fetch.get_df_selected_tf(
                config["general"]["ticker"],
                config["general"]["interval"],
                config["general"]["startDate"],
                config["general"]["endDate"],
            )
        else:
            df, ticker = fetch.get_df_recent(
                config["general"]["ticker"],
                config["general"]["interval"],
                config["general"]["timePeriod"],
            )
    else:
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        csv_path = os.path.join(root_path, config["general"]["dummyCsvFileName"])

        df = pd.read_csv(csv_path, parse_dates=True, index_col=0)

        ticker = "Custom"

    ma_period = config["indicators"]["maPeriod"]
    rsi_period = config["indicators"]["rsiPeriod"]
    atr_period = config["indicators"]["atrPeriod"]
    std_dev_period = config["indicators"]["stdDevPeriod"]

    cutoff_period = max(ma_period, rsi_period, atr_period, std_dev_period)

    datetimes = df.index.to_series()
    closes = df.iloc[:, 0]
    highs = df.iloc[:, 1]
    lows = df.iloc[:, 2]
    opens = df.iloc[:, 3]
    rsi = []
    sma = []
    atr = []
    std_dev = []
    entries = []
    exits = []
    ongoing_balance = []
    stoploss_regions = []
    takeprofit_regions = []

    data_obj = api.GraphData(
        account,
        ticker,
        datetimes,
        closes,
        highs,
        lows,
        opens,
        ma_period,
        rsi_period,
        atr_period,
        std_dev_period,
        cutoff_period,
        sma,
        rsi,
        atr,
        std_dev,
        entries,
        exits,
        ongoing_balance,
        stoploss_regions,
        takeprofit_regions,
    )

    data_obj.calc_rsi()
    data_obj.calc_atr()
    data_obj.calc_sma()
    data_obj.calc_std_dev()
    data_obj.sma = data_obj.sma[cutoff_period:]
    data_obj.rsi = data_obj.rsi[cutoff_period:]
    data_obj.atr = data_obj.atr[cutoff_period:]
    data_obj.std_dev = data_obj.std_dev[cutoff_period:]

    data_obj.datetimes = df.index.to_series()[cutoff_period:]
    data_obj.closes = df.iloc[:, 0][cutoff_period:]
    data_obj.highs = df.iloc[:, 1][cutoff_period:]
    data_obj.lows = df.iloc[:, 2][cutoff_period:]
    data_obj.opens = df.iloc[:, 3][cutoff_period:]

    if not account.check_balance():
        print("\nError: Base order value cannot be greater than starting amount. Please restart the server.\n")
        quit()

    if config["general"]["addCsv"]:
        number = utils.generate_number(4)
        df.to_csv(f"z.{data_obj.ticker}_{number}.csv")

    data_obj.entries, data_obj.exits, stoploss_regions, takeprofit_regions = (
        order.indicators(account, data_obj)
    )
    data_obj.stoploss_regions = stoploss_regions
    data_obj.takeprofit_regions = takeprofit_regions

    account.win_rate = (
        (account.profitable_trades / account.completed_trades * 100)
        if account.completed_trades > 0
        else -1
    )

    if account.win_rate == -1:
        win_rate_str = "N/A"
        perc = ""
    else:
        win_rate_str = round(account.win_rate, 2)
        perc = "%"

    if account.profit > 0:
        profit_colour = "\033[32m"
    elif account.profit < 0:
        profit_colour = "\033[31m"
    else:
        profit_colour = "\033[0m"
    reset_colour = "\033[0m"

    print(
        "\n=====================================================================================\n"
    )
    total_return = ((account.balance_absolute / config['account']['initialBalance']) - 1) * 100
    print(
        f"Made {account.completed_trades} trades | Win rate: {win_rate_str}{perc} | "
        f"{profit_colour}Return: {total_return:.2f}%{reset_colour} | "
        f"{profit_colour}Profit: ${account.profit:.2f}{reset_colour}\n"
    )

    return data_obj


def init_sim_data(account):
    config = fetch.get_settings()

    if not config["general"]["dummyData"]:
        try:
            df, ticker = fetch.get_df_selected_tf(
                config["general"]["ticker"],
                config["general"]["interval"],
                config["general"]["startDate"],
                config["general"]["endDate"],
            )
        except Exception as e:
            print(f"Failed to run simulations: {e}")
            quit()
    else:
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        csv_path = os.path.join(root_path, config["general"]["dummyCsvFileName"])

        df = pd.read_csv(csv_path, parse_dates=True, index_col=0)

        ticker = "Custom"

    ma_period = config["indicators"]["maPeriod"]
    rsi_period = config["indicators"]["rsiPeriod"]
    atr_period = config["indicators"]["atrPeriod"]
    std_dev_period = config["indicators"]["stdDevPeriod"]

    cutoff_period = max(ma_period, rsi_period, atr_period, std_dev_period)

    datetimes = df.index.to_series()
    closes = df.iloc[:, 0]
    highs = df.iloc[:, 1]
    lows = df.iloc[:, 2]
    opens = df.iloc[:, 3]
    rsi = []
    sma = []
    atr = []
    std_dev = []
    entries = []
    exits = []
    ongoing_balance = []
    stoploss_regions = []
    takeprofit_regions = []

    data_obj = api.GraphData(
        account,
        ticker,
        datetimes,
        closes,
        highs,
        lows,
        opens,
        ma_period,
        rsi_period,
        atr_period,
        std_dev_period,
        cutoff_period,
        sma,
        rsi,
        atr,
        std_dev,
        entries,
        exits,
        ongoing_balance,
        stoploss_regions,
        takeprofit_regions,
    )

    data_obj.calc_rsi()
    data_obj.calc_atr()
    data_obj.calc_sma()
    data_obj.calc_std_dev()
    data_obj.sma = data_obj.sma[cutoff_period:]
    data_obj.rsi = data_obj.rsi[cutoff_period:]
    data_obj.atr = data_obj.atr[cutoff_period:]
    data_obj.std_dev = data_obj.std_dev[cutoff_period:]

    data_obj.datetimes = df.index.to_series()[cutoff_period:]
    data_obj.closes = df.iloc[:, 0][cutoff_period:]
    data_obj.highs = df.iloc[:, 1][cutoff_period:]
    data_obj.lows = df.iloc[:, 2][cutoff_period:]
    data_obj.opens = df.iloc[:, 3][cutoff_period:]

    data_obj.entries, data_obj.exits, stoploss_regions, takeprofit_regions = (
        order.indicators(account, data_obj)
    )
    data_obj.stoploss_regions = stoploss_regions
    data_obj.takeprofit_regions = takeprofit_regions

    account.profit = account.balance_absolute - config["account"]["initialBalance"]

    valid = account.check_balance()
    if valid == False:
        print(
            "\nError: Base order value cannot be greater than starting amount. Please restart the server.\n"
        )
        quit()

    return data_obj


def init_backtest_data(all_backtests, account, i):
    config = fetch.get_settings()

    df, ticker = fetch.get_df_selected_tf(
        all_backtests[i]["ticker"],
        config["general"]["interval"],
        config["general"]["startDate"],
        config["general"]["endDate"],
    )

    ma_period = all_backtests[i]["ma_period"]
    rsi_period = all_backtests[i]["rsi_period"]
    atr_period = all_backtests[i]["atr_period"]
    std_dev_period = all_backtests[i]["std_dev_period"]

    cutoff_period = max(ma_period, rsi_period, atr_period, std_dev_period)

    datetimes = df.index.to_series()
    closes = df.iloc[:, 0]
    highs = df.iloc[:, 1]
    lows = df.iloc[:, 2]
    opens = df.iloc[:, 3]
    rsi = []
    sma = []
    atr = []
    std_dev = []
    entries = []
    exits = []
    ongoing_balance = []
    stoploss_regions = []
    takeprofit_regions = []

    data_obj = api.GraphData(
        account,
        ticker,
        datetimes,
        closes,
        highs,
        lows,
        opens,
        ma_period,
        rsi_period,
        atr_period,
        std_dev_period,
        cutoff_period,
        sma,
        rsi,
        atr,
        std_dev,
        entries,
        exits,
        ongoing_balance,
        stoploss_regions,
        takeprofit_regions,
    )

    data_obj.calc_rsi()
    data_obj.calc_atr()
    data_obj.calc_sma()
    data_obj.calc_std_dev()
    data_obj.sma = data_obj.sma[cutoff_period:]
    data_obj.rsi = data_obj.rsi[cutoff_period:]
    data_obj.atr = data_obj.atr[cutoff_period:]
    data_obj.std_dev = data_obj.std_dev[cutoff_period:]

    data_obj.datetimes = df.index.to_series()[cutoff_period:]
    data_obj.closes = df.iloc[:, 0][cutoff_period:]
    data_obj.highs = df.iloc[:, 1][cutoff_period:]
    data_obj.lows = df.iloc[:, 2][cutoff_period:]
    data_obj.opens = df.iloc[:, 3][cutoff_period:]

    data_obj.entries, data_obj.exits, stoploss_regions, takeprofit_regions = (
        order.indicators(account, data_obj)
    )
    data_obj.stoploss_regions = stoploss_regions
    data_obj.takeprofit_regions = takeprofit_regions

    account.profit = account.balance_absolute - config["account"]["initialBalance"]

    valid = account.check_balance()
    if valid == False:
        print(
            "\nError: Base order value cannot be greater than starting amount. Please restart the server.\n"
        )
        quit()

    return data_obj
