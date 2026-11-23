from decimal import Decimal, InvalidOperation

OPTIONS = (
    "USD to INR",
    "INR to USD",
    "Miles to km",
    "Km to miles",
    "Kilograms to pounds",
    "Pounds to kilograms",
)


def convert(amount, mode, rate):
    try:
        value = Decimal(amount)
        factor = (
            Decimal(rate)
            if mode in OPTIONS[:2]
            else Decimal("1.609344")
            if mode in OPTIONS[2:4]
            else 1 / Decimal("0.45359237")
        )
        if not value.is_finite() or not factor.is_finite() or factor <= 0:
            raise ValueError
        output = value * factor if OPTIONS.index(mode) % 2 == 0 else value / factor
        return f"{output:,.4f} {mode.split()[-1]}"
    except (InvalidOperation, ValueError):
        raise ValueError(
            "Enter a finite amount and a positive exchange rate for currency."
        ) from None


if __name__ == "__main__":
    from forms import form

    form(
        "Currency and units",
        [
            ("Amount", ""),
            ("Conversion", OPTIONS),
            ("INR per USD (supply your rate)", ""),
        ],
        {"Convert": convert},
    )
