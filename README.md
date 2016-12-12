# Graduation_project_selection_site
The site for graduation project selection

## How to deploy

The site uses Python and Nginx as back-end and MariaDB(MySQL) as the database, javascript and html as the front-end.

### Python

The needed packages of python are: Tornado, mysql.connector, openpyxl
To install the packages using pip to install tornado and openpyxl
```python
pip install tornado openpyxl
```
Then download the mysql connector from http://dev.mysql.com/downloads/connector/python/ and install as the orcale's instruction.

Actually, you can download the source code and install it by

```bash
cd /path/to/the/source/code
pip install .
```

### Nginx

See the nginx.conf as the sample of configuration and config the /etc/nginx/nginx.conf file as needed

### Run

Change directory to the root of the program, and run
```
python main.py
```
Then visit the site configured as your nginx.conf. (In this sample, visit localhost:8080)

***

### Development guidelines

#### Encoding

To guarantee UTF-8 compliance on different platforms, especially for Python source files containing non-ASCII characters, please add the following comment to the beginning of .py files:

```python
  # coding=UTF-8
```

See [PEP 263](https://www.python.org/dev/peps/pep-0263/) for details.
