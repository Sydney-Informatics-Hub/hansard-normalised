from bs4 import BeautifulSoup

from . import Parser, HTMLParseException


class ParserDefault(Parser):
    """
    Minimal Parser that simple strips HTML tags and sets all content as speech with no metadata.
    """
    @staticmethod
    def _parse_html(html_document: str) -> dict[str, list[str]]:
        html_stripped: str = BeautifulSoup(html_document, "lxml").text
        return {'speaker_id': [''], 'speaker': [''], 'speech': [html_stripped]}
