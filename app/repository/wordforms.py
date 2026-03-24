import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from io import TextIOWrapper
from fastapi import UploadFile, HTTPException
from pymorphy3 import MorphAnalyzer
from collections import defaultdict
from openpyxl import Workbook

OUTPUT_DIR = Path('data_out')

@dataclass
class LemmaStats:
    total: int
    lines: dict[int, int]


morph = MorphAnalyzer()


def get_lemma(word: str, cache_words: dict[str, str]) -> str:
    if word not in cache_words:
        lemma = morph.parse(word)[0].normal_form
        cache_words[word] = lemma
        return lemma
    return cache_words[word]


def count_lemmas_in_line(line: str, cache_words: dict[str, str]) -> dict[str, int]:

    words = re.findall(r"[а-яё]+", line.lower())
    line_cnt = defaultdict(int)

    for word in words:
        lemma = get_lemma(word=word, cache_words=cache_words)
        line_cnt[lemma] += 1

    return line_cnt


def update_stats_for_lemma(stats: dict[str, LemmaStats], lemma: str, count: int, line_id: int) -> None:
    if lemma not in stats:
        stats[lemma] = LemmaStats(total=0, lines={})
    if count != 0:
        stats[lemma].total += count
        stats[lemma].lines[line_id] = count


def analyze_wordforms_in_file(file: UploadFile) -> tuple[dict[str, LemmaStats], int]:
    stats: dict[str, LemmaStats] = {}
    cache_words: dict[str, str] = {}
    line_id = 0
    with TextIOWrapper(file.file, encoding='utf-8') as textfile:
        for line in textfile:
            line_cnt = count_lemmas_in_line(line=line, cache_words=cache_words)
            for lemma, count in line_cnt.items():
                update_stats_for_lemma(stats=stats, lemma=lemma, count=count, line_id=line_id)
            line_id += 1
    return stats, line_id


def ensure_directory_exists(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def format_line_counts(stats_row: dict[int, int], cnt_rows: int) -> str:
    return ','.join((str(stats_row.get(i, 0)) for i in range(cnt_rows)))


def build_excel_row(lemma: str, total: int, stats_row: dict[int, int], cnt_rows: int) -> list[str | int]:
    return [lemma, total, format_line_counts(stats_row=stats_row, cnt_rows=cnt_rows)]


def create_excel_table(stats: dict[str, LemmaStats], cnt_rows: int) -> str:
    wb = Workbook(write_only=True)
    ws = wb.create_sheet(title='Wordforms')
    ws.append(['Словоформа', 'Количество во всем документе', 'Количество в каждой строке'])
    for lemma, lemma_stats in stats.items():
        ws.append(
            build_excel_row(lemma=lemma,
                            total=lemma_stats.total,
                            stats_row=lemma_stats.lines,
                            cnt_rows=cnt_rows)
        )
    filename = f'result_{uuid.uuid4()}.xlsx'
    ensure_directory_exists(path=OUTPUT_DIR)
    wb.save(OUTPUT_DIR / filename)
    return filename


def validate_filename(filename: str | None) -> None:
    if filename is None:
        raise HTTPException(status_code=400, detail='Invalid filename')
    if filename == '' or not filename.lower().endswith('.txt'):
        raise HTTPException(status_code=400, detail='File format is not supported')


def validate_not_empty(file: UploadFile) -> None:
    if file.file.read(1) == b"":
        file.file.seek(0)
        raise HTTPException(status_code=400, detail='File is empty')
    file.file.seek(0)

def validate_content_type(content_type: str | None) -> None:
    if content_type != 'text/plain':
        raise HTTPException(status_code=400, detail='Invalid content type file')


def validate_encoding(file: UploadFile) -> None:
    try:
        file.file.read(2048).decode('utf-8')
    except UnicodeError:
        raise HTTPException(400, "File must be UTF-8 encoded")
    finally:
        file.file.seek(0)


def validate_file(file: UploadFile) -> None:
    validate_filename(file.filename)
    validate_content_type(file.content_type)
    validate_not_empty(file)
    validate_encoding(file)
