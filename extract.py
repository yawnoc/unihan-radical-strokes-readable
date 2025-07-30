#!/usr/bin/env python3
import re
from pathlib import Path

KANGXI_RADICALS = ''.join(chr(code_point) for code_point in range(0x2F00, 0x2FD6))


class Character:
    def __init__(self, code_point: str, ideograph: str, indexes: tuple['Index', ...]):
        self.code_point = code_point
        self.ideograph = ideograph
        self.indexes = indexes

    def tsv_line(self) -> str:
        return f'{self.code_point}\t{self.ideograph}\t{", ".join(str(index) for index in self.indexes)}\n'


class Index:
    def __init__(self, radical_number: int, stroke_count: int):
        self.radical_number = radical_number
        self.stroke_count = stroke_count

    def __str__(self):
        return f'{KANGXI_RADICALS[self.radical_number - 1]} + {self.stroke_count}'


def main():
    text_content = Path('Unihan_IRGSources.txt').read_text()
    characters = [
        Character(
            code_point=f"U+{line_match.group('code_point_hex')}",
            ideograph=chr(int(line_match.group('code_point_hex'), 16)),
            indexes=tuple(
                Index(
                    radical_number=int(index_match.group('radical_number')),
                    stroke_count=int(index_match.group('stroke_count')),
                )
                for index_string in line_match.group('index_run').split()
                if (
                    index_match := re.match(
                        pattern=r"(?P<radical_number>\d+)'*\.(?P<stroke_count>-?\d+)",
                        string=index_string,
                    )
                )
            ),
        )
        for line_match in re.finditer(
            pattern=r'^U\+(?P<code_point_hex>[0-9A-F]+)\tkRSUnicode\t(?P<index_run>[\-\d. ]+)$',
            string=text_content,
            flags=re.MULTILINE,
        )
    ]

    tsv_content = ''.join(character.tsv_line() for character in characters)
    Path('unihan-radical-strokes-readable.tsv').write_text(tsv_content)


if __name__ == '__main__':
    main()
