import api.fetch as api
import math


def bearish_comeback(candles, period):
    config = api.get_settings()
    current_candle = candles[-1]
    most_recent_candle = candles[-2]

    price_difference = candles[-(period + 1)]["open"] - most_recent_candle["open"]
    ratio = price_difference / most_recent_candle["std_dev"]

    A = config["strategy1"]["A"]
    B = config["strategy1"]["B"]
    threshold = A - (B * math.log(period + 1))

    is_bearish = most_recent_candle["close"] < most_recent_candle["open"]

    if ratio > threshold and is_bearish:
        return {
            "buy": True,
            "price": current_candle["open"],
            "amount": config["account"]["baseOrderValue"] * ratio,
        }

    return {"buy": False}
