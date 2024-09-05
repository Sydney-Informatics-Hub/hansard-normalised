from . import Parser, HTMLParseException


class ParserRevision1(Parser):
    """
    Parser covering years 1901 - 1988
    """
    @staticmethod
    def _parse_html(html_document: str) -> dict[str, list[str]]:
        raise HTMLParseException("Not implemented")
