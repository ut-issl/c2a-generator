import csv
from pathlib import Path


def generate(src_path: str, dest_path: Path, base_id: int) -> None:
    assert dest_path.parent.exists(), f"{dest_path} does not exist"
    with open(src_path, "r", encoding="utf-8") as csv_file, open(dest_path, "w", encoding="utf-8") as header_file:
        header_file.write(
            """
/**
 * @file
 * @brief  EH の Rule 共通ヘッダ
 */
#ifndef EVENT_HANDLER_RULES_H_
#define EVENT_HANDLER_RULES_H_

/**
 * @enum  EH_RULE_ID
 * @brief EH_Rule の ID
 * @note  最大数は EH_RULE_MAX で規定
 * @note  uint16_t を想定
 */
typedef enum
{
"""[
                1:
            ]
        )
        reader = csv.reader(csv_file)
        headers = next(reader)
        dict_reader = csv.DictReader(csv_file, fieldnames=headers)
        name_list = []
        for row in dict_reader:
            if not any(row):
                continue
            try:
                if row["name"] in name_list:
                    continue
                header_file.write(f'  {row["name"]} = {base_id},\n')
                name_list.append(row["name"])
                base_id += 1
            except ValueError:
                continue
        header_file.write(
            """
} EH_RULE_ID;


/**
 * @brief  event_handler のデフォルトルールを読み込む
 * @param  void
 * @return void
 */
void EH_load_default_rules(void);

#endif
"""[
                1:
            ]
        )
