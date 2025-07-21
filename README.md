# backdoorme

This repository provides automation to patch open source projects and
build Docker images containing the patched binaries.

## Usage

```
make patch/<name>   # clone, patch and build the project
make image/<name>   # build a Docker image using the patched binary
```

Example for HashiCorp Vault:

```
make patch/hashicorp-vault
make image/hashicorp-vault
```
## Log Dashboard

A simple Flask web application is included to view `.out` log files under the `logs/` directory. It aggregates numbered log files per folder and provides a timeline view.

Binary content within log files is detected using `charset-normalizer`. Any non-text data is shown as hexadecimal for safety.


### Running

```bash
pip install -r requirements.txt
python webapp/app.py
```

Then open `http://localhost:5000` in your browser.
