from datetime import datetime
from decimal import Decimal
from forms import form
from services import get_json


class Tracker:
    previous = None

    def quote(self):
        data = get_json("https://api.coinbase.com/v2/prices/BTC-USD/spot")
        price = Decimal(data["data"]["amount"])
        change = (
            ""
            if self.previous is None
            else f"\nChange since last refresh: {price - self.previous:+,.2f} USD"
        )
        self.previous = price
        return f"BTC · {price:,.2f} USD{change}\nCoinbase · {datetime.now():%H:%M:%S}"


if __name__ == "__main__":
    form(
        "Bitcoin spot price",
        [],
        {"Refresh": Tracker().quote},
        threaded=True,
        refresh=30000,
    )
