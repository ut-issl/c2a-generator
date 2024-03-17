import csv
from pathlib import Path


def generate(bct_src: list, dest_file_path: Path) -> None:
    prev_row0_is_none = False
    dest_line_len = 12
    dest_line_max = 300
    line_index = 2

    with open(dest_file_path, "w", encoding="utf-8") as dest_file:
        dest_file.write(
            """
Comment,Name,ShortName,BCID,エイリアス,,,,,Danger Flag,Description,Note
,,,,Deploy,SetBlockPosition,Clear,Activate,Inactivate,,,
"""[
                1:
            ]
        )
        bcid = 0
        for src_path, bcid_base in bct_src:
            if bcid_base is not None:
                bcid = bcid_base
            with open(src_path, "r", encoding="utf-8") as src_file:
                reader = csv.reader(src_file)
                next(reader)

                for row in reader:
                    row = row[1:]
                    row = [row[i].replace("\n", "##") for i in range(len(row))]
                    row = [row[i].replace(",", "@@") for i in range(len(row))]
                    if not any(row):
                        continue
                    dest_file.write(f",{row[0]},,{bcid},,,,,,,{row[1]},\n")
                    bcid += 1
                    line_index += 1

        dest_file.write(("," * (dest_line_len - 1) + "\n") * (dest_line_max - line_index))
