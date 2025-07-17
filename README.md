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