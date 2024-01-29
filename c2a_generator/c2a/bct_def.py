import csv
from pathlib import Path


def generate(src_path: Path, dest_path: Path) -> None:
    with open(src_path, "r", encoding="utf-8") as csv_file, open(dest_path, "w", encoding="utf-8") as header_file:
        header_file.write(
            """
/**
 * @file
 * @brief  ブロックコマンド定義
 * @note   このコードは自動生成されています！
 */
#ifndef BLOCK_COMMAND_DEFINITIONS_H_
#define BLOCK_COMMAND_DEFINITIONS_H_

// 登録されるBlockCommandTableのblock番号を規定
typedef enum
{
"""[
                1:
            ]
        )
        reader = csv.reader(csv_file)
        next(reader)
        previous_line_was_comment = False
        for row in reader:
            if not any(row):
                continue
            if row[0]:
                previous_line_was_comment = False
                comment = f"    // {row[2]}" if len(row) > 2 and row[2] else ""
                header_file.write(f"  {row[1]} = {row[0]},{comment}\n")
            else:
                if not previous_line_was_comment:
                    header_file.write("\n")
                header_file.write(f"  // {row[1]}\n")
                previous_line_was_comment = True
        header_file.write(
            """
  BC_ID_MAX    // BCT 自体のサイズは BCT_MAX_BLOCKS で規定
} BC_DEFAULT_ID;

void BC_load_defaults(void);

#endif
"""
        )
