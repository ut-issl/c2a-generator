import csv
from pathlib import Path

from .util import get_git_file_blob_url


def generate(src_path: str, dest_path: Path) -> None:
    file_blob_url = get_git_file_blob_url(src_path)
    with open(dest_path, "w", encoding="utf-8") as header_file:
        header_file.write(
            f"""
/**
 * @file
 * @brief  テレメトリ定義
 * @note   このコードは自動生成されています！
 * @src    {file_blob_url}
 */
#ifndef TELEMETRY_DEFINITIONS_H_
#define TELEMETRY_DEFINITIONS_H_

typedef enum
{{
"""[
                1:
            ]
        )
        tlm_codes = []
        for csv_file in src_path.glob("*.csv"):
            with csv_file.open("r", encoding="utf-8") as file:
                reader = csv.reader(file)
                try:
                    packet_id = next(reader)[1]
                except StopIteration:
                    continue
                packet_id_hex = f"0x{int(packet_id):02X}"
                tlm_codes.append((packet_id_hex, csv_file.stem))
        tlm_codes.sort(key=lambda x: x[0])
        for packet_id, file_name in tlm_codes:
            header_file.write(f"  Tlm_CODE_{file_name} = {packet_id},\n")
        header_file.write(
            """
  TLM_CODE_MAX
} TLM_CODE;

#endif
"""
        )
