import csv
from pathlib import Path


def generate(src_path: str, dest_path: Path, eh_header: str) -> None:
    assert dest_path.parent.exists(), f"{dest_path} does not exist"
    with open(src_path, "r", encoding="utf-8") as csv_file, open(dest_path, "w", encoding="utf-8") as src_file:
        src_file.write(
            f"""
#pragma section REPRO
/**
 * @file
 * @brief  EH の Rule 共通コード
 */
{eh_header}

void EH_load_default_rules(void)
{{
  EH_RuleSettings settings;

"""[
                1:
            ]
        )
        reader = csv.reader(csv_file)
        headers = next(reader)
        dict_reader = csv.DictReader(csv_file, fieldnames=headers)
        for row in dict_reader:
            if row[headers[0]].startswith('#'):
                continue
            if not any(row):
                continue
            code = ""
            if row["description"]:
                row_description = row["description"].replace("\n", "\n// ")
                code += f"  // {row_description}\n"
            code += f"  settings.event.group = {row['group']};\n"
            code += f"  settings.event.local = {row['local']};\n"
            code += f"  settings.event.err_level = EL_ERROR_LEVEL_{row['err_level']};\n"
            code += f"  settings.should_match_err_level = {1 if row['should_match_err_level'] == 'TRUE' else 0};\n"
            code += f"  settings.condition.type = EH_RESPONSE_CONDITION_{row['type'].upper()};\n"
            code += f"  settings.condition.count_threshold = {row['count_threshold']};\n"
            code += f"  settings.condition.time_threshold_ms = {int(float(row['time_threshold[s]']) * 1000)};\n"
            code += f"  settings.deploy_bct_id = {row['bc']};\n"
            code += f"  settings.is_active = {1 if row['is_active'] == 'TRUE' else 0};\n"
            code += f"  EH_register_rule({row['name']}, &settings);\n\n"
            src_file.write(code)
        src_file.write(
            """}
}

#pragma section
"""[
                1:
            ]
        )
