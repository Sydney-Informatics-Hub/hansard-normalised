import traceback
from typing import Optional

from . import HTMLParseException


class Parser:
    """
    An interface for Hansard HTML Parser implementations. Follows the Chain of Responsibility pattern,
    such that Parser1 will attempt to parse the document first in the following: Parser1(Parser2(Parser3()))
    """
    def __init__(self, next_parser: Optional['Parser'] = None):
        self._next_parser: Optional['Parser'] = next_parser

    def parse(self, html_document: str) -> dict[str, list[str]]:
        """
        This method attempts to parse the provided HTML document. If the implemented _parse_html method fails, the specified _next_parser is called to parse the document.
        The method should either return a valid value or raise an HTMLParseException
        :param html_document: The HTML document to be parsed as a string
        :type html_document: str
        :return: A dictionary containing utterances and the associated metadata of the utterances
        :rtype: dict[str, list[str]]
        """
        try:
            # First the current Parser implementation attempts to parse the document
            return self._parse_html(html_document)
        except HTMLParseException:
            if not self._next_parser:
                # If the current Parser cannot parse the document, and there is no subsequent Parser set, then the document cannot be parsed
                raise HTMLParseException('No Parser could parse this document')
        except Exception:
            if not self._next_parser:
                raise HTMLParseException(f'Unexpected error while parsing this document: {traceback.format_exc()}')

        return self._next_parser.parse(html_document)

    @staticmethod
    def _parse_html(html_document: str) -> dict[str, list[str]]:
        """
        This method should be implemented by subclasses of Parser. The method should either return a valid value or raise an HTMLParseException
        :param html_document: The HTML document to be parsed as a string
        :type html_document: str
        :return: A dictionary containing utterances and the associated metadata of the utterances
        :rtype: dict[str, list[str]]
        """
        raise NotImplementedError()
