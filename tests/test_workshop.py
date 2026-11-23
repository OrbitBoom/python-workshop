import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "desktop"))
from cipher import shift
from converter import convert
from morse import encode, decode
from paint import export
from services import translate, search
from bitcoin import Tracker
from email_client import send


class WorkshopTests(unittest.TestCase):
    def test_numeric_shift_round_trip(self):
        text = "wrap z!@#$  café 123"
        self.assertEqual(shift(shift(text, "908"), "908", -1), text)
        for key in ("", "3a"):
            with self.assertRaises(ValueError):
                shift(text, key)

    def test_morse_words_and_punctuation(self):
        self.assertEqual(decode(encode("SOS, call 9/1.")), "SOS, CALL 9/1.")
        with self.assertRaises(ValueError):
            decode("... ----xx")

    def test_units_and_rate(self):
        self.assertEqual(convert("2", "Miles to km", ""), "3.2187 km")
        self.assertEqual(convert("200", "INR to USD", "80"), "2.5000 USD")
        for amount, rate in [("NaN", "2"), ("2", "0"), ("", "")]:
            with self.assertRaises(ValueError):
                convert(amount, "USD to INR", rate)

    def test_drawing_exports_clicks_and_strokes(self):
        data = export(
            200, 150, "#fff", [("#abc", 4, [(5, 5)]), ("#def", 8, [(1, 1), (7, 9)])]
        )
        svg = ET.fromstring(data)
        self.assertEqual(
            [item.tag.split("}")[-1] for item in svg], ["rect", "circle", "polyline"]
        )
        self.assertEqual(svg[-1].attrib["points"], "1,1 7,9")

    def test_last_price_updates_after_every_quote(self):
        tracker = Tracker()
        with patch(
            "bitcoin.get_json",
            side_effect=[{"data": {"amount": n}} for n in ("10", "13", "12")],
        ):
            tracker.quote()
            self.assertIn("+3.00", tracker.quote())
            self.assertIn("-1.00", tracker.quote())

    def test_service_responses(self):
        with patch(
            "services.get_json",
            return_value={
                "query": {"pages": {"1": {"title": "Python", "extract": "Language"}}}
            },
        ):
            self.assertEqual(search("python"), "Python\n\nLanguage")
        with patch(
            "services.get_json",
            return_value={
                "responseStatus": "200",
                "responseData": {"translatedText": "c&#39;est"},
            },
        ):
            self.assertEqual(translate("it is", "en", "fr"), "c'est")

    def test_translation_prefers_exact_match(self):
        data = {
            "responseStatus": 200,
            "responseData": {"translatedText": "partial"},
            "matches": [
                {"segment": "Hello", "match": 0.99, "translation": "partial"},
                {"segment": "Hello", "match": 1, "translation": "नमस्कार"},
            ],
        }
        with patch("services.get_json", return_value=data):
            self.assertEqual(translate("Hello", "en", "hi"), "नमस्कार")

    def test_email_content(self):
        with patch("email_client.smtplib.SMTP_SSL") as transport:
            send(
                "sender@example.org",
                "sample",
                "reader@example.org",
                "Test subject",
                "Body",
            )
            message = transport.return_value.__enter__.return_value.send_message.call_args.args[
                0
            ]
            self.assertEqual(message["Subject"], "Test subject")
            self.assertEqual(message.get_content(), "Body\n")

    def test_terminal_win_draw_and_invalid_input(self):
        for moves, outcome in [
            ("oops T1 T1 M1 T2 M2 T3", "X wins!"),
            ("T1 T2 T3 M2 M1 M3 B2 B1 B3", "Draw."),
        ]:
            result = subprocess.run(
                [sys.executable, ROOT / "games/tic_tac_toe.py"],
                input="\n".join(moves.split()),
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn(outcome, result.stdout)


if __name__ == "__main__":
    unittest.main()
