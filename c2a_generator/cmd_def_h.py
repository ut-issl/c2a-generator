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
 * @brief  コマンド定義
 * @note   このコードは自動生成されています！
 * @src    {file_blob_url}
 */
#ifndef COMMAND_DEFINITIONS_H_
#define COMMAND_DEFINITIONS_H_

typedef enum
{{
"""[
                1:
            ]
        )
        reader = csv.reader(csv_file)
        headers = next(reader)
        dict_reader = csv.DictReader(csv_file, fieldnames=headers)
        code = 0
        for row in dict_reader:
            if not any(row):
                continue
            if row["enabled"] == "TRUE":
                try:
                    row["code"] = f"0x{int(code):04X}"
                    code += 1
                except ValueError:
                    continue
                # comment = f"    // {row[16]}" if len(row) > 2 and row[16] else ""
                comment = ""
                header_file.write(f'  Cmd_CODE_{row["name"]} = {row["code"]},{comment}\n')
        header_file.write(
            """
  Cmd_CODE_MAX
} CMD_CODE;

#endif
"""
        )
