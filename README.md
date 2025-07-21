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

Folder names are normalized to uppercase so directories such as `at`, `aT` and
`AT` are consolidated under `AT`. If duplicate file names exist across these
folders their contents are shown sequentially.

Binary content within log files is detected using `charset-normalizer`. Any non-text data is displayed in a hexdump style format for safety.


### Running Manually

```bash
pip install -r requirements.txt
python webapp/app.py
```

Then open `http://localhost:5000` in your browser.

### Installing as a Service

Both the Exodus DNS server and the log dashboard can be managed by
`systemd`. Each directory contains an `install.sh` script that sets up
the service:

```bash
sudo ./exodus/install.sh
sudo ./webapp/install.sh
```

After running these scripts the `exodus.service` and `webapp.service`
units will be installed and started automatically.
