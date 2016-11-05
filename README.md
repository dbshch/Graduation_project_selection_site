# Graduation_project_selection_site
The site for graduation project selection

## How to deploy

The site uses Python and Nginx as back-end and MariaDB(MySQL) as the database, javascript and html as the front-end.

### Python

The needed packages of python are: Tornado, mysql.connector
To install the packages using pip to install tornado
```python
pip install tornado
```
Then download the mysql connector from http://dev.mysql.com/downloads/connector/python/ and install as the orcale's instruction.

### Nginx

See the nginx.conf as the sample of configuration and config the /etc/nginx/nginx.conf file as needed

### Run

Change directory to the root of the program, and run
```
python main.py
```
Then visit the site configured as your nginx.conf. (In this sample, visit localhost:13000)
