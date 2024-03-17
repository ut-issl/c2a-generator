import argparse
from pathlib import Path

import c2a_generator
import toml


def main(root_path: str, toml_path: str, export_wings: bool = False) -> None:
    config = toml.load(toml_path)
    assert config.get("obc") is not None, "obc is not defined in config.toml"
    assert config.get("c2a_user_root") is not None, "c2a_root is not defined in config.toml"
    c2a_user_path = root_path / config["c2a_user_root"]

    for obc in config["obc"]:
        if obc.get("is_main_obc"):
            c2a_generator.bct_def_h.generate(root_path / obc["bct_src"], c2a_user_path / "TlmCmd/block_command_definitions.h")
            c2a_generator.cmd_def_h.generate(root_path / obc["cmd_src"], c2a_user_path / "TlmCmd/command_definitions.h")
            c2a_generator.cmd_def_c.generate(root_path / obc["cmd_src"], c2a_user_path / "TlmCmd/command_definitions.c")
            c2a_generator.tlm_def_h.generate(root_path / obc["tlm_src"], c2a_user_path / "TlmCmd/telemetry_definitions.h")
            c2a_generator.tlm_def_c.generate(root_path / obc["tlm_src"], c2a_user_path / "TlmCmd/telemetry_definitions.c")
            if export_wings:
                c2a_generator.cmd_csv.generate(root_path / obc["cmd_src"], root_path / obc["cmd_wings_dest"])
                c2a_generator.bct_csv.generate(root_path / obc["bct_src"], root_path / obc["bct_wings_dest"])
                c2a_generator.tlm_csv.generate(root_path / obc["tlm_src"], root_path / obc["tlm_wings_dest"], obc["tlm_prefix"])
        elif obc.get("is_enable"):
            key_list = ["driver_path", "name", "driver_type", "driver_name", "max_tlm_num", "code_when_tlm_not_found"]
            for key in key_list:
                assert obc.get(key) is not None, f"{key} is not defined in config.toml"
            c2a_generator.subobc_cmd_def_h.generate(
                root_path / obc["cmd_src"],
                c2a_user_path / "Driver" / obc["driver_path"] / f"{obc['name'].lower()}_command_definitions.h",
                obc_name=obc["name"].upper(),
            )
            c2a_generator.subobc_tlm_def_h.generate(
                root_path / obc["tlm_src"],
                c2a_user_path / "Driver" / obc["driver_path"] / f"{obc['name'].lower()}_telemetry_definitions.h",
                obc_name=obc["name"].upper(),
            )
            c2a_generator.subobc_tlm_buf_c.generate(
                root_path / obc["tlm_src"],
                c2a_user_path / "Driver" / obc["driver_path"] / f"{obc['name'].lower()}_telemetry_buffer.c",
                obc_name=obc["name"].upper(),
                driver_type=obc["driver_type"],
                driver_name=obc["driver_name"],
                code_when_tlm_not_found=obc["code_when_tlm_not_found"],
            )
            c2a_generator.subobc_tlm_buf_h.generate(
                root_path / obc["tlm_src"],
                c2a_user_path / "Driver" / obc["driver_path"] / f"{obc['name'].lower()}_telemetry_buffer.h",
                obc_name=obc["name"].upper(),
                driver_type=obc["driver_type"],
                driver_name=obc["driver_name"],
                max_tlm_num=obc["max_tlm_num"],
            )
            c2a_generator.subobc_tlm_data_def_h.generate(
                root_path / obc["tlm_src"],
                c2a_user_path / "Driver" / obc["driver_path"] / f"{obc['name'].lower()}_telemetry_data_definitions.h",
                obc["name"].upper(),
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--wings", action="store_true", default=False, help="Perform special processing when --wings is specified")
    parser.add_argument("--config", type=str, required=True, help="Path to the config TOML file")
    args = parser.parse_args()

    toml_path = Path(args.config)
    if not toml_path.exists():
        print(f"Error: The specified config file does not exist at {toml_path}")
    else:
        root_path = toml_path.parent
        main(root_path, toml_path, args.wings)
