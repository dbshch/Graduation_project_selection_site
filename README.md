# Graduation_project_selection_site

The site for graduation project selection in UM-SJTU JI.

## Dependencies

We need

- python3
- Tornado
- mysql.connector
- openpyxl
- PyYaml

To install them,

```python
pip install tornado openpyxl PyYaml
```

Then download the mysql connector from http://dev.mysql.com/downloads/connector/python/ and install as the orcale's instruction.

Actually, you can download the source code and install it by

```bash
cd /path/to/the/source/code
pip install .
```

## Run

Firstly, clone the repo. We do not need `npm` now since dependencies have been added into this repo now (will be removed).

```
git clone https://github.com/dbshch/Graduation_project_selection_site.git
cd Graduation_project_selection_site
# npm install
```

Secondly, specify your database and localhost config.

```
cp config.yaml.example config.yaml
vim config.yaml
```

and type your own config. Now, run the server

```
python main.py
```

and visit <http://localhost:8080>. The port is set in `config.yaml`.

## Deployment

See the nginx.conf as the sample of configuration and config the /etc/nginx/nginx.conf file as needed.
