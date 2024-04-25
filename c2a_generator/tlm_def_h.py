import csv
from pathlib import Path


def generate(src_path: str, dest_path: Path) -> None:
    with open(dest_path, "w", encoding="utf-8") as header_file:
        header_file.write(
            """
/**
 * @file
 * @brief  テレメトリ定義
 * @note   このコードは自動生成されています！
 */
#ifndef TELEMETRY_DEFINITIONS_H_
#define TELEMETRY_DEFINITIONS_H_

typedef enum
{
"""[1:]
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
