import csv
from pathlib import Path


def generate(src_path: Path, dest_path: Path) -> None:
    with open(src_path, "r", encoding="utf-8") as csv_file, open(dest_path, "w", encoding="utf-8") as header_file:
        header_file.write(
            """
/**
 * @file
 * @brief  コマンド定義
 * @note   このコードは自動生成されています！
 */
#ifndef COMMAND_DEFINITIONS_H_
#define COMMAND_DEFINITIONS_H_

typedef enum
{
"""[
                1:
            ]
        )
        reader = csv.reader(csv_file)
        next(reader)
        for row in reader:
            if not any(row):
                continue
            if row[0]:
                try:
                    row[0] = f"0x{int(row[0]):04X}"
                except ValueError:
                    continue
                # comment = f"    // {row[16]}" if len(row) > 2 and row[16] else ""
                comment = ""
                header_file.write(f"  Cmd_CODE_{row[2]} = {row[0]},{comment}\n")
        header_file.write(
            """
  Cmd_CODE_MAX
} CMD_CODE;

#endif
"""
        )
