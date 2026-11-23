"""A repeating numeric shift for experimenting with reversible text transformations."""

from string import ascii_lowercase

ALPHABET = ascii_lowercase + "!@#$ "


def shift(text, key, direction=1):
    if not key or any(ch not in "0123456789" for ch in key):
        raise ValueError("Enter one or more digits for the key.")
    result = []
    for i, char in enumerate(text):
        if char in ALPHABET:
            offset = int(key[i % len(key)]) * direction
            char = ALPHABET[(ALPHABET.index(char) + offset) % len(ALPHABET)]
        result.append(char)
    return "".join(result)


if __name__ == "__main__":
    from forms import form

    form(
        "Numeric shift cipher",
        [("Message", ""), ("Digit key", "")],
        {"Encode": shift, "Decode": lambda text, key: shift(text, key, -1)},
    )
