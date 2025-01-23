import plotly.graph_objects as go
from plotly.subplots import make_subplots
import api.fetch as fetch
import core
import core.data
from core.Account import Account
from core.Backtest import Backtest
import utils.variables
import numpy as np
import utils.convert as convert


def build():
    config = fetch.get_settings()

    account = Account(
        uninvested_balance=config["account"]["initialBalance"],
        balance_absolute=config["account"]["initialBalance"],
        orders=[],
        profit=0,
        open_position_amount=0,
        total_invested=0,
        shares_owned=0,
        win_rate=0,
        completed_trades=0,
        profitable_trades=0,
        open_positions=0,
    )

    data = core.data.init_graph_data(account)
    data.datetimes, data.opens, data.closes, data.highs, data.lows = (
        convert.series_to_lists(data)
    )

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.8, 0.2],
        subplot_titles=[f"{data.ticker} US Equity", "Average True Range (ATR)"],
    )

    candlestick = go.Candlestick(
        x=data.datetimes,
        open=data.opens,
        high=data.highs,
        low=data.lows,
        close=data.closes,
        name="Price ($)",
        increasing=dict(line=dict(color="#16a16e")),
        decreasing=dict(line=dict(color="#eb4034")),
        increasing_fillcolor="#16a16e",
        decreasing_fillcolor="#eb4034",
        hovertext=data.std_dev,
    )

    sma_line = go.Scatter(
        x=data.datetimes,
        y=data.sma,
        mode="lines",
        name="SMA",
        line=dict(color="orange", width=1),
    )

    fig.add_trace(candlestick, row=1, col=1)
    fig.add_trace(sma_line, row=1, col=1)

    fig.add_trace(
        go.Scatter(
            x=data.entries.index,
            y=data.entries,
            mode="markers",
            name="BUY",
            marker_symbol="arrow-up",
            marker_size=8,
            marker_line_width=1,
            marker_line_color="#eee",
            marker_color="#0ac91d",
            hovertemplate="BUY: %{y}",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=data.exits.index,
            y=data.exits,
            mode="markers",
            name="SELL",
            marker_symbol="arrow-down",
            marker_size=8,
            marker_line_width=1,
            marker_line_color="#eee",
            marker_color="#b0160e",
            hovertemplate="SELL: %{y}",
        ),
        row=1,
        col=1,
    )

    if config["general"]["renderStoplossTakeprofit"] == True:
        for region in data.takeprofit_regions:
            fig.add_shape(
                type="rect",
                x0=region["x0"],
                x1=region["x1"],
                y0=region["y0"],
                y1=region["y1"],
                fillcolor=region["fillcolor"],
                opacity=region["opacity"],
                line=dict(width=0),
            )

        for region in data.stoploss_regions:
            fig.add_shape(
                type="rect",
                x0=region["x0"],
                x1=region["x1"],
                y0=region["y0"],
                y1=region["y1"],
                fillcolor=region["fillcolor"],
                opacity=region["opacity"],
                line=dict(width=0),
            )

    atr_line = go.Scatter(
        x=data.datetimes,
        y=data.atr,
        mode="lines",
        name="ATR",
        line=dict(color="#1f77b4", width=2),
    )
    fig.add_trace(atr_line, row=2, col=1)

    fig.update_layout(
        title_text=f"{data.ticker}",
        xaxis=dict(gridcolor="#1b1b1b", type="category"),
        xaxis2=dict(title="Date", gridcolor="#1b1b1b"),
        yaxis=dict(title="Price ($)", gridcolor="#1b1b1b"),
        yaxis2=dict(title="ATR", gridcolor="#1b1b1b"),
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
    )

    return fig


def simulate():
    print("Working...\n")

    ongoing_balances = []
    chart_lines = []
    all_backtests = []
    all_graph_data = []

    config = fetch.get_settings()

    if config["simulate"]["simBestBacktests"] == False:
        iterations = config["simulate"]["simulations"]
    else:
        all_best_backtests = utils.variables.load_best_backtests()
        if len(all_best_backtests) > 0:
            iterations = len(all_best_backtests)
        else:
            print(
                "Cannot perform simulation on best backtests when there are none. Please restart the server."
            )
            quit()
    for i in range(iterations):

        account = Account(
            uninvested_balance=config["account"]["initialBalance"],
            balance_absolute=config["account"]["initialBalance"],
            orders=[],
            profit=0,
            open_position_amount=0,
            total_invested=0,
            shares_owned=0,
            win_rate=0,
            completed_trades=0,
            profitable_trades=0,
            open_positions=0,
        )

        utils.variables.randomise()
        config = fetch.get_settings()

        if config["simulate"]["simBestBacktests"] == False:
            data = core.data.init_sim_data(account)
        else:
            try:
                data = core.data.init_backtest_data(all_best_backtests, account, i)
            except:
                print(
                    "Could not simulate existing backtest results. Has the file best backtests JSON file been populated?"
                )

        win_rate = (
            ((account.profitable_trades / account.completed_trades) * 100)
            if account.completed_trades > 0
            else -1
        )
        account.win_rate = win_rate

        # If new random backtests are being generated
        if config["simulate"]["simBestBacktests"] == True:
            backtest_result = Backtest(
                unique_id=utils.variables.generate_uid(6),
                ticker=all_best_backtests[i]["ticker"],
                sim_period=len(data.closes),
                total_investment=config["account"]["initialBalance"],
                final_amount=round(account.balance_absolute, 2),
                total_return=round(
                    (
                        (account.balance_absolute - config["account"]["initialBalance"])
                        / config["account"]["initialBalance"]
                        * 100
                    ),
                    2,
                ),
                win_rate=round(win_rate, 2),
                ma_period=all_best_backtests[i]["ma_period"],
                rsi_period=all_best_backtests[i]["rsi_period"],
                atr_period=all_best_backtests[i]["atr_period"],
                std_dev_period=all_best_backtests[i]["std_dev_period"],
                max_order_value=all_best_backtests[i]["max_order_value"],
                max_concurrent_positions=all_best_backtests[i][
                    "max_concurrent_positions"
                ],
                buy_multiplier=round(all_best_backtests[i]["buy_multiplier"], 2),
                band_multiplier=round(all_best_backtests[i]["band_multiplier"], 2),
                A_strategy_1=round(all_best_backtests[i]["A_strategy_1"], 2),
                B_strategy_1=round(all_best_backtests[i]["B_strategy_1"], 2),
                stoploss_atr_multiplier=round(
                    all_best_backtests[i]["stoploss_atr_multiplier"], 2
                ),
                takeprofit_atr_multiplier=round(
                    all_best_backtests[i]["takeprofit_atr_multiplier"], 2
                ),
            )

        # If existing backtests are being used
        else:
            backtest_result = Backtest(
                unique_id=utils.variables.generate_uid(6),
                ticker=config["general"]["ticker"],
                sim_period=len(data.closes),
                total_investment=config["account"]["initialBalance"],
                final_amount=round(account.balance_absolute, 2),
                total_return=round(
                    (
                        (account.balance_absolute - config["account"]["initialBalance"])
                        / config["account"]["initialBalance"]
                        * 100
                    ),
                    2,
                ),
                win_rate=round(win_rate, 2),
                ma_period=config["indicators"]["maPeriod"],
                rsi_period=config["indicators"]["rsiPeriod"],
                atr_period=config["indicators"]["atrPeriod"],
                std_dev_period=config["indicators"]["stdDevPeriod"],
                max_order_value=config["account"]["maxOrderValue"],
                max_concurrent_positions=config["account"]["maxConcurrentPositions"],
                buy_multiplier=round(config["multipliers"]["buyMultiplier"], 2),
                band_multiplier=round(config["multipliers"]["bandMultiplier"], 2),
                A_strategy_1=round(config["strategy1"]["A"], 2),
                B_strategy_1=round(config["strategy1"]["B"], 2),
                stoploss_atr_multiplier=round(
                    config["multipliers"]["stoplossAtrMultiplier"], 2
                ),
                takeprofit_atr_multiplier=round(
                    config["multipliers"]["takeprofitAtrMultiplier"], 2
                ),
            )

        line = go.Scatter(
            x=data.datetimes,
            y=data.ongoing_balance,
            mode="lines",
            name="Balance",
            line=dict(color=utils.variables.random_colour(), width=1),
            hovertemplate="$%{y}\n %{x}"
            + f"Sim {backtest_result.unique_id}. Total return: {backtest_result.total_return:.2f}%.",
        )

        all_backtests.append(backtest_result)
        ongoing_balances.append(data.ongoing_balance)

        chart_lines.append(line)
        all_graph_data.append(data)
        print(f"Finished simulation {(i + 1)}/{iterations}")

    final_amounts = []
    total_returns = []

    for backtest in all_backtests:
        final_amounts.append(backtest.final_amount)
        total_returns.append(backtest.total_return)

    all_line_lengths = [
        len(graph_data.ongoing_balance) for graph_data in all_graph_data
    ]
    shortest_line_length = min(all_line_lengths)
    for graph_data in all_graph_data:
        graph_data.ongoing_balance = graph_data.ongoing_balance[
            (len(graph_data.ongoing_balance) - shortest_line_length) :
        ]
        graph_data.datetimes.to_list()
        graph_data.datetimes = graph_data.datetimes[
            (len(graph_data.datetimes) - shortest_line_length) :
        ]

    final_amounts_percentile = np.percentile(
        final_amounts, config["simulate"]["topResultsPercentile"]
    )
    total_returns_percentile = np.percentile(
        total_returns, config["simulate"]["topResultsPercentile"]
    )

    top_backtests_count = 0
    new_best_backtests = []
    for result in all_backtests:
        if (
            result.final_amount > final_amounts_percentile
            or result.total_return > total_returns_percentile
        ) and config["simulate"]["simBestBacktests"] == False:
            if config["simulate"]["addToTopResults"] == True:
                utils.variables.add_to_top_results(result)
            top_backtests_count += 1
        elif (
            result.final_amount > final_amounts_percentile
            or result.total_return > total_returns_percentile
        ) and config["simulate"]["simBestBacktests"] == True:
            new_best_backtests.append(result)
            top_backtests_count += 1

    if config["simulate"]["simBestBacktests"] == True:
        utils.variables.overwrite_top_results(new_best_backtests)

    for i in range(len(chart_lines)):
        chart_lines[i]["y"] = ongoing_balances[i]

    if config["simulate"]["writeBacktestsToJSON"] == True:
        simulation_id = utils.variables.write_to_json(all_backtests)
    else:
        simulation_id = utils.variables.generate_uid(6)
    print(
        f"\nSimulation {simulation_id} complete. {top_backtests_count} backtests committed to best results.\n\n======================================================================"
    )

    fig = go.Figure(data=chart_lines)

    fig.update_layout(
        title=f"{data.ticker} US Equity",
        xaxis_title="Date",
        yaxis_title="Balance",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        xaxis=dict(
            type="category",
            tickmode="linear",
            dtick=(len(data.closes) / 10),
            gridcolor="#262626",
        ),
        yaxis=dict(gridcolor="#262626"),
        showlegend=False,
    )

    return fig
