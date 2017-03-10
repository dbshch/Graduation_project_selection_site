#!/bin/bash

echo "Database name:"
read dbName
echo "Username:"
read username
echo "Password:"
read -s pwd
echo "Server port:"
read port

cat << EOF > config.yaml
# database
database: $dbName
user: $username
password: $pwd

# dev-server
port: $port
EOF

pip3 install tornado openpyxl PyYaml

if ! python -c "import mysql.connector" > /dev/null 2>&1; then
    wget https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.5.tar.gz
    tar -zxf mysql-connector-python-2.1.5.tar.gz
    (
        cd mysql-connector-python-2.1.5
        python3 setup.py install
    )
fi