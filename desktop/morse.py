MORSE_CODE_DICT = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    ",": "--..--",
    ".": ".-.-.-",
    "?": "..--..",
    "/": "-..-.",
    "-": "-....-",
    "(": "-.--.",
    ")": "-.--.-",
}

REVERSE = {value: key for key, value in MORSE_CODE_DICT.items()}


def encode(text):
    try:
        return " / ".join(
            " ".join(MORSE_CODE_DICT[c] for c in word) for word in text.upper().split()
        )
    except KeyError as exc:
        raise ValueError(f"Unsupported character: {exc.args[0]}") from None


def decode(code):
    try:
        return " ".join(
            "".join(REVERSE[c] for c in word.split()) for word in code.split("/")
        )
    except KeyError as exc:
        raise ValueError(f"Unknown Morse sequence: {exc.args[0]}") from None


if __name__ == "__main__":
    from forms import form

    form(
        "Morse code",
        [("Text or Morse (use / between words)", "")],
        {"Encode": encode, "Decode": decode},
    )
