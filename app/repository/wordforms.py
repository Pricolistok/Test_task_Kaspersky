import re
from dataclasses import dataclass
from io import TextIOWrapper
from typing import BinaryIO

from pymorphy3 import MorphAnalyzer
from collections import defaultdict
from openpyxl import Workbook

from app.repository.queue import queue_files, update_job
from app.repository.utils import ensure_directory_exists, OUTPUT_DIR, UPLOAD_DIR


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


def analyze_wordforms_in_file(file: BinaryIO) -> tuple[dict[str, LemmaStats], int]:
    stats: dict[str, LemmaStats] = {}
    cache_words: dict[str, str] = {}
    line_id = 0
    with TextIOWrapper(file, encoding='utf-8') as textfile:
        for line in textfile:
            line_cnt = count_lemmas_in_line(line=line, cache_words=cache_words)
            for lemma, count in line_cnt.items():
                update_stats_for_lemma(stats=stats, lemma=lemma, count=count, line_id=line_id)
            line_id += 1
    return stats, line_id


def format_line_counts(stats_row: dict[int, int], cnt_rows: int) -> str:
    return ','.join((str(stats_row.get(i, 0)) for i in range(cnt_rows)))


def build_excel_row(lemma: str, total: int, stats_row: dict[int, int], cnt_rows: int) -> list[str | int]:
    return [lemma, total, format_line_counts(stats_row=stats_row, cnt_rows=cnt_rows)]


def create_excel_table(stats: dict[str, LemmaStats], cnt_rows: int, filename: str) -> None:
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
    filename = f'{filename}.xlsx'
    ensure_directory_exists(path=OUTPUT_DIR)
    wb.save(OUTPUT_DIR / filename)


def worker() -> None:
    while True:
        job = queue_files.get()
        try:
            with open(UPLOAD_DIR / f'data_in_{job.task_id}.txt', 'rb') as file:
                update_job(job, 'processing','Wordforms analysis',)
                stats, cnt_rows = analyze_wordforms_in_file(file=file)
                update_job(job, 'processing', 'Build excel')
                create_excel_table(stats=stats, cnt_rows=cnt_rows, filename=str(job.task_id))
                update_job(job, 'done', 'Excel table was completed')
        except Exception as e:
            update_job(job, 'failed', str(e))
        finally:
            queue_files.task_done()
