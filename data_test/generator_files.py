import random

words = [
    "житель", "жителем", "город", "города", "машина", "машиной",
    "человек", "люди", "дом", "дома", "кот", "кота"
]


def generate_file(filename: str, lines: int, words_per_line: int):
    with open(filename, "w", encoding="utf-8") as f:
        for _ in range(lines):
            line = " ".join(random.choice(words) for _ in range(words_per_line))
            f.write(line + "\n")


generate_file(
    filename="tester.txt",
    lines=5_000_000,
    words_per_line=20
)