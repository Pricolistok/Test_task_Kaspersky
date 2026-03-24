import re
import pandas as pd
from io import TextIOWrapper
from fastapi import UploadFile
from pymorphy3 import MorphAnalyzer
from collections import defaultdict


morph = MorphAnalyzer()

def analysis_row(line: str) -> defaultdict:
    words = re.findall(r"[а-яё]+", line.lower())
    line_cnt = defaultdict(int)

    for word in words:
        lemma = morph.parse(word)[0].normal_form
        line_cnt[lemma] += 1

    return line_cnt

def transform_file(file: UploadFile) -> list[str]:
    return TextIOWrapper(file.file, encoding='utf-8').readlines()

def analysis_wordforms(file: UploadFile) -> dict:
    stats = {}
    lines = transform_file(file=file)
    for line_id, line in enumerate(lines):
        line_cnt = analysis_row(line=line)

        for lemma, count in line_cnt.items():
            if lemma not in stats:
                stats[lemma] = [0, [0] * len(lines)]

            stats[lemma][0] += count
            stats[lemma][1][line_id] = count

    return stats


def create_table(stats: dict[str, list]):
    rows = []
    for lemma, (total, stats_row) in stats.items():
        rows.append([lemma, total, ",".join(map(str, stats_row))])
    df = pd.DataFrame(rows, columns=['Словоформа', 'Количество во всем документе', 'Количество в каждой строке'])
    df.to_excel('result.xlsx', index=False)


def checker_format_file(file: UploadFile):
    return file.content_type == 'text/plain'
