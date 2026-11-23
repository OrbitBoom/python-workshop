from forms import form
from services import translate

if __name__ == "__main__":
    languages = (
        "en",
        "hi",
        "fr",
        "de",
        "es",
        "it",
        "ja",
        "pt",
        "zh-CN",
        "ar",
        "bn",
        "gu",
    )
    form(
        "Translation",
        [
            ("Text sent to MyMemory", ""),
            ("From (language code)", languages),
            ("To (language code)", languages[1:] + languages[:1]),
        ],
        {"Translate": translate},
        threaded=True,
    )
