from pathlib import Path
from typing import Union, Optional

from tqdm import tqdm
from pandas import DataFrame
import sqlite3

import parsers as ps


class CorpusBuilder:
    def __init__(self, source_db_path: Union[Path, str], dest_db_path: Union[Path, str], progress_bar: Optional[tqdm] = None):
        if isinstance(source_db_path, str):
            source_db_path = Path(source_db_path)
        if isinstance(dest_db_path, str):
            dest_db_path = Path(dest_db_path)

        self.source_db_path: Path = source_db_path
        self.dest_db_path: Path = dest_db_path
        self.progress_bar: Optional[tqdm] = progress_bar

        self.parser_chain: ps.Parser = ps.ParserRevision1(ps.ParserDefault())

    def parse_speech_contents(self, max_entries: Optional[int] = None) -> DataFrame:
        if (max_entries is not None) and (max_entries < 1):
            raise ValueError(f"max_entries must either be None or a value greater than 0. Provided value is {max_entries}")
        corpus_data = {'page_id': [], 'date': [], 'speaker_id': [], 'speaker': [], 'speech': []}

        conn = sqlite3.connect(self.source_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        total_entries_query = "SELECT COUNT(*) FROM proceedings_page"
        cursor.execute(total_entries_query)
        total_entries = cursor.fetchone()[0]

        query = "SELECT page_id, date, page_html FROM proceedings_page ORDER BY date ASC;"
        cursor.execute(query)

        row = cursor.fetchone()
        rows_read: int = 0
        if self.progress_bar:
            self.progress_bar.reset(total=total_entries)
            self.progress_bar.set_description("entries parsed")
        while (row is not None) and ((max_entries is None) or (rows_read < max_entries)):
            rows_read += 1
            if self.progress_bar:
                self.progress_bar.update()
            try:
                html_data = self.parser_chain.parse(row['page_html'])
            except ps.HTMLParseException:
                row = cursor.fetchone()
                continue

            corpus_data['speaker_id'].append(html_data['speaker_id'])
            corpus_data['speaker'].append(html_data['speaker'])
            corpus_data['speech'].append(html_data['speech'])
            corpus_data['page_id'].append(row['page_id'])
            corpus_data['date'].append(row['date'])
            row = cursor.fetchone()

        conn.close()

        return DataFrame(data=corpus_data)

    def write_to_db(self, corpus_df: DataFrame):
        conn = sqlite3.connect(self.dest_db_path)
        corpus_df.to_sql('speech', conn, if_exists='append', index=False)
        conn.close()


if __name__ == "__main__":
    tqdm_obj = tqdm()
    corpus_builder = CorpusBuilder(source_db_path=('./tidy_hansard.db'), dest_db_path=('./parsed_hansard.db'), progress_bar=tqdm_obj)
    hansard_df: DataFrame = corpus_builder.parse_speech_contents()
    corpus_builder.write_to_db(hansard_df)
