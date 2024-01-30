from pathlib import Path

import c2a
import toml

root_path = Path(__file__).parent.parent
toml_path = root_path / "c2a_generator_config.toml"
config = toml.load(toml_path)
assert config.get("obc") is not None, "obc is not defined in config.toml"
assert config.get("c2a_user_root") is not None, "c2a_root is not defined in config.toml"
c2a_user_path = root_path / config["c2a_user_root"]


def main() -> None:
    for obc in config["obc"]:
        if obc.get("is_main_obc"):
            c2a.bct_def_h.generate(root_path / obc["bct_src"], c2a_user_path / "TlmCmd/block_command_definitions.h")
            c2a.cmd_def_h.generate(root_path / obc["cmd_src"], c2a_user_path / "TlmCmd/command_definitions.h")
            c2a.cmd_def_c.generate(root_path / obc["cmd_src"], c2a_user_path / "TlmCmd/command_definitions.c")
            c2a.tlm_def_h.generate(root_path / obc["tlm_src"], c2a_user_path / "TlmCmd/telemetry_definitions.h")
            c2a.tlm_def_c.generate(root_path / obc["tlm_src"], c2a_user_path / "TlmCmd/telemetry_definitions.c")
        elif obc.get("is_enable"):
            key_list = ["driver_path", "name", "driver_type", "driver_name", "max_tlm_num", "code_when_tlm_not_found"]
            for key in key_list:
                assert obc.get(key) is not None, f"{key} is not defined in config.toml"
            c2a.subobc_cmd_def_h.generate(
                root_path / obc["cmd_src"],
                c2a_user_path / "Driver" / obc["driver_path"] / f"{obc['name'].lower()}_command_definitions.h",
                obc_name=obc["name"].upper(),
            )
            c2a.subobc_tlm_def_h.generate(
                root_path / obc["tlm_src"],
                c2a_user_path / "Driver" / obc["driver_path"] / f"{obc['name'].lower()}_telemetry_definitions.h",
                obc_name=obc["name"].upper(),
            )
            c2a.subobc_tlm_buf_c.generate(
                root_path / obc["tlm_src"],
                c2a_user_path / "Driver" / obc["driver_path"] / f"{obc['name'].lower()}_telemetry_buffer.c",
                obc_name=obc["name"].upper(),
                driver_type=obc["driver_type"],
                driver_name=obc["driver_name"],
                code_when_tlm_not_found=obc["code_when_tlm_not_found"],
            )
            c2a.subobc_tlm_buf_h.generate(
                root_path / obc["tlm_src"],
                c2a_user_path / "Driver" / obc["driver_path"] / f"{obc['name'].lower()}_telemetry_buffer.h",
                obc_name=obc["name"].upper(),
                driver_type=obc["driver_type"],
                driver_name=obc["driver_name"],
                max_tlm_num=obc["max_tlm_num"],
            )
            c2a.subobc_tlm_data_def_h.generate(
                root_path / obc["tlm_src"],
                c2a_user_path / "Driver" / obc["driver_path"] / f"{obc['name'].lower()}_telemetry_data_definitions.h",
                obc["name"].upper(),
            )


if __name__ == "__main__":
    main()
