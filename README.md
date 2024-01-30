# Tools

This directory contains various tools for tasks such as conversion.

## Runtime Environment

- The tools require `rye` to run.

## Setup

To set up your environment, follow these steps:

```bash
# Assuming execution from the ./tools directory
cp ../.github/hooks/pre-commit ../.git/hooks # Copy the pre-commit file to set it up
rye sync
```

## Usage

### Generating C2A Code

1. Modify the `c2a_generator_config.toml` file according to your needs.
2. Run the following commands:

```bash
rye run c2a_generator
```

### Generating CSV from Past Telemetry CSV Files

1. Adjust the settings in `csv_converter_config.toml`.
2. Execute the following commands:

```bash
rye run tlm_csv_converter
```

---

This README provides clear instructions on the environment setup and usage of the tools within the directory. It's structured to be user-friendly and straightforward, guiding users through the necessary steps for both setting up the environment and executing the tools.
