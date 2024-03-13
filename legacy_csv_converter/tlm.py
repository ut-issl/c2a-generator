import csv
import logging
from pathlib import Path

import toml

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def transform_csv(src_path: Path, dest_path: Path) -> None:
    with open(src_path, "r", encoding="utf-8") as src_file, open(dest_path, "w", encoding="utf-8", newline="") as dest_file:
        reader = csv.reader(src_file)
        writer = csv.writer(dest_file)

        first_row_component = ["", 0, "", ""]
        first_row_component[2] = next(reader)[2]
        data = next(reader)
        first_row_component[1] = int(data[2], 16)
        first_row_component[3] = data[3].replace("##", "\n").replace("@@", ",")
        first_row_component[0] = "TRUE" if next(reader)[2] == "ENABLE" else "FALSE"
        writer.writerow(first_row_component)
        for i in range(5):
            next(reader)
        writer.writerow(
            ["subsystem", "name", "type", "bit", "var", "conv", "a0", "a1", "a2", "a3", "a4", "a5", "status", "description", "note", "priority"]
        )
        for row in reader:
            if not any(row):  # 空行をスキップ
                continue

            name = row[1]
            if len(row[7]) > 0 and row[7][0] != "=":
                bit = row[7]
                if row[2] != "||":
                    type_ = f"_{row[2]}"
                else:
                    type_ = ""
            else:
                bit = ""
                if row[2] == "||":
                    type_ = ""
                else:
                    type_ = row[2]
            var = row[3].replace("@@", ",") if row[3] and row[3] != "||" else ""
            conv = row[8] if row[8] else ""
            a0, a1, a2, a3, a4, a5 = row[9:15]
            status = row[15].replace("@@", ",") if row[15] else ""
            description = row[16].replace("@@", ",") if row[16] else ""
            note = row[17].replace("@@", ",") if row[17] else ""

            writer.writerow(["", name, type_, bit, var, conv, a0, a1, a2, a3, a4, a5, status, description, note, ""])


def main() -> None:
    config_path = Path(__file__).parent.parent / "legacy_csv_converter_config.toml"
    config = toml.load(config_path)
    assert config.get("tlm") is not None, "tlm section is not defined in csv_converter_config.toml"
    config = config.get("tlm", {})
    assert config.get("src_path") is not None, "src_path is not defined in csv_converter_config.toml"
    assert config.get("dest_path") is not None, "dest_path is not defined in csv_converter_config.toml"
    assert config.get("src_prefix") is not None, "src_prefix is not defined in csv_converter_config.toml"

    src_path = Path(config["src_path"])
    dest_path = Path(config["dest_path"])
    src_prefix = config["src_prefix"]

    if not dest_path.exists():
        logger.info(f"Destination path {dest_path} does not exist. Creating...")
        dest_path.mkdir(parents=True)

    for src_file in src_path.glob(src_prefix + "*.csv"):
        dest_file = dest_path / src_file.name.replace(src_prefix, "")
        transform_csv(src_file, dest_file)
        logger.info(f"File {src_file.name} has been processed and saved to {dest_file}")


if __name__ == "__main__":
    main()
