import api.fetch as api


class Rules:
    def __init__(self, payload):
        self.payload = payload
        self.config = api.get_settings()

    def balance_valid(self):
        initial_buy_amount = self.payload["initial_buy_amount"]
        max_order_value = self.config["account"]["maxOrderValue"]
        uninvested_balance = self.payload["account"].uninvested_balance

        initial_buy_amount = min(initial_buy_amount, max_order_value, uninvested_balance)

        return {
            "valid": initial_buy_amount > 0,
            "amount": initial_buy_amount
        }

    def max_positions_reached(self):
        account = self.payload["account"]
        max_positions = self.config["account"]["maxConcurrentPositions"]
        return account.open_positions < max_positions

    def validate(self):
        balance_result = self.balance_valid()
        return {
            "balance_valid": balance_result["valid"],
            "max_positions_reached": self.max_positions_reached(),
        }
