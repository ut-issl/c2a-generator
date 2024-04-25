import csv
from pathlib import Path


def generate(src_path: Path, dest_path: Path, obc_name: str) -> None:
    assert dest_path.parent.exists(), f"{dest_path} does not exist"
    with open(src_path, "r", encoding="utf-8") as csv_file, open(
        dest_path, "w", encoding="utf-8"
    ) as header_file:
        header_file.write(
            f"""
/**
 * @file
 * @brief  コマンド定義
 * @note   このコードは自動生成されています！
 */
#ifndef {obc_name}_COMMAND_DEFINITIONS_H_
#define {obc_name}_COMMAND_DEFINITIONS_H_

typedef enum
{{
"""[1:]
        )
        reader = csv.reader(csv_file)
        headers = next(reader)
        dict_reader = csv.DictReader(csv_file, fieldnames=headers)
        for row in dict_reader:
            if not any(row):
                continue
            if row["code"]:
                try:
                    row["code"] = f"0x{int(row['code']):04X}"
                except ValueError:
                    continue
                header_file.write(
                    f"  {obc_name}_Cmd_CODE_{row['name']} = {row['name']},\n"
                )
        header_file.write(
            f"""
  {obc_name}_Cmd_CODE_MAX
}} {obc_name}_CMD_CODE;

#endif
"""
        )
