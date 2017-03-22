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

pip3 install tornado openpyxl PyYaml mysql-connector-python

mysql -u"$username" -p"$password" "$dbName" < ./sample.dump