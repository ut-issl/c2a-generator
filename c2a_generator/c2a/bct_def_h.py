import csv
from pathlib import Path

from .util import get_git_file_blob_url


def generate(src_path: str, dest_path: Path) -> None:
    file_blob_url = get_git_file_blob_url(src_path)
    assert dest_path.parent.exists(), f"{dest_path} does not exist"

    with open(src_path, "r", encoding="utf-8") as csv_file, open(dest_path, "w", encoding="utf-8") as header_file:
        header_file.write(
            f"""
/**
 * @file
 * @brief  ブロックコマンド定義
 * @note   このコードは自動生成されています！
 * @src    {file_blob_url}
 */
#ifndef BLOCK_COMMAND_DEFINITIONS_H_
#define BLOCK_COMMAND_DEFINITIONS_H_

// 登録されるBlockCommandTableのblock番号を規定
typedef enum
{{
"""[
                1:
            ]
        )
        reader = csv.reader(csv_file)
        headers = next(reader)
        dict_reader = csv.DictReader(csv_file, fieldnames=headers)
        previous_line_was_comment = False
        for row in dict_reader:
            if not any(row):
                continue
            if row["bcid"]:
                previous_line_was_comment = False
                comment = f"    // {row['description']}" if len(row) > 2 and row["description"] else ""
                header_file.write(f"  {row['name']},{comment}\n")
            else:
                if not previous_line_was_comment:
                    header_file.write("\n")
                header_file.write(f"  // {row['name']}\n")
                previous_line_was_comment = True
        header_file.write(
            """
  BC_ID_MAX    // BCT 自体のサイズは BCT_MAX_BLOCKS で規定
} BC_DEFAULT_ID;

void BC_load_defaults(void);

#endif
"""
        )
