import csv
from pathlib import Path

from .util import get_git_file_blob_url


def generate(src_path: Path, dest_path: Path, obc_name: str) -> None:
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
#ifndef {obc_name}_COMMAND_DEFINITIONS_H_
#define {obc_name}_COMMAND_DEFINITIONS_H_

typedef enum
{{
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
                header_file.write(f"  {obc_name}_Cmd_CODE_{row[2]} = {row[0]},\n")
        header_file.write(
            f"""
  {obc_name}_Cmd_CODE_MAX
}} {obc_name}_CMD_CODE;

#endif
"""
        )
