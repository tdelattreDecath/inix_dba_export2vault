# VAULT EXPORT

## Export data from excel to Vault

### Please use a python3 virtual environment:

```shell script
python3 -m venv venv
source venv/bin/activate

# install requirements
pip install -r requirements.txt 
```

### Usage

``` shell script
# export required environment variables
export VAULT_ADDR='https//.....'
export VAULT_TOKEN=XXXXXXXXXXXXXXXXXX

./vault_export.py
```

### What does it do ?

Parses the xlsx file, sorts it as a python dictonary.

Then gets the current secrets from Vault and updates them with the data found in the xlsx file.

Pushes the changes to Vault
