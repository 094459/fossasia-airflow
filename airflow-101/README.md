## Demo Setup

**For a local MYSQL setup**

Run up a local MySQL database which has the following connection settings

```
finch|docker run --name mysql -d \
   -p 3306:3306 \
   -e MYSQL_ROOT_PASSWORD=change-me \
   --restart unless-stopped \
   mysql:8
```

You can connect to this MySql server running on 127.0.0.1:3306, connecting as root with a password of change-me. You can also create a connection from within VSCode.

> *Tip!* If you get errors such as "ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/tmp/mysql.sock' (2)", use the "--protocol tcp" 

You will need to enable access to your MySQL database from Airflow. Running this worked for me. **Remember, this is only playing around/demo, never never ever do this for something in real life**

```
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'change-me';
SET GLOBAL local_infile=1;
FLUSH PRIVILEGES;
```

**For a local PostgreSQL setup**

Run up a local PostgreSQL database by creating the follder Docker Compose file (as postgres-local.yml)

```
version: '3'
volumes:
  psql:
services:
  psql:
    image: postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: change-me
    volumes:
      - psql:/var/lib/postgresql/data 
    ports:
      - 5555:5432
```

```
finch|docker compose -p local-postgres -f postgres-local.yml up
```

This will make postgres avilable locally on port 5555, with the username of postgres/change-me


**Setting up Airflow stuff**

Once you have Airflow up and running, you need to set up the following in the default_aws connection, under the extras add the following based on your aws region

{"region_name": "eu-west-1"}

**MySQL**

You need to configure the default_mysql as follows

```
hostname - host.docker.internal (Docker) / 192.168.5.2 (Finch)
database - bad_jokes
login - root
password - change-me
port - 3306
Extras - {"local_infile": "true"}
```

**PostgreSQL**

```
hostname - host.docker.internal (Docker) / 192.168.5.2 (Finch)
database - bad_jokes
login - postgres
password - change-me
port - 5555

```

> Apache Airflow provider is downgraded as a bug that seems to ignore the local_infile was introduced. 3.2.1 is an older, known working version of the provider
