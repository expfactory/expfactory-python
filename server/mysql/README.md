# Expfactory Server (MySQL)

This will provide a static (MySQL) server setup, that can either be run on a server natively (locally), or with a MySQL Dockerized database. Instructions for composer are included below:

- Integration with [Concerto](https://github.com/campsych/concerto-platform/wiki):

The basic instructions are also included here.


## Customizing your MySQL Server
This is primarily intended for development, and if you would like a complete Dockerized application we recommend either using expfactory-docker or submitting a PR to this repo.  The following command, run from this directory, will set up a mysql database available on port 3306 called `expfactory-mysql`

	docker run \
	--detach \
	--name=expfactory-mysql \
	--env="MYSQL_ROOT_PASSWORD=composer" \
	--publish 6603:3306 \
	--volume=conf.d:/etc/mysql/conf.d \
	--volume=data:/var/lib/mysql \
	mysql

After doing the above, you will want to copy the sql file into the container, and run it to configure the database:


      docker cp create_test_database.sql expfactory-mysql:/create_test_database.sql
      docker cp create_expfactory_table.sql expfactory-mysql:/create_expfactory_table.sql
      docker exec -it expfactory-mysql bash -c "mysql --user=root --password=composer < create_test_database.sql"			
      docker exec -it expfactory-mysql bash -c "mysql --user=concerto --password=concerto < create_expfactory_table.sql"

You of course (are recommended) to set up a proper database. If you use the setup provided above, continue. Otherwise, be sure to change the host/etc credentials in `database_connect.php` and to run `create_expfactory_table.sql`.


## Generating the battery
If you have a server that can serve static files and want to deploy experiments using a MySQL database, this is the solution you should try. The batteries themselves are stored as static html files with a uid parameter in the query string to pass the subject id: e.g. `https://mywebserver/itest/digit_span-en/?uid=123456789`

PHP scripts, also hosted by the web server, are called on experiment completion to save the results (in JSON format) to your MySQL database.

This folder contains the required server resources to deploy.
Ensure to define your database connection parameters in `database_connect.php.`
In this folder, you will also find a [create_expfactory_table.sql](create_expfactory_table.sql) and a [concerto.conf](concerto.conf) file as an example of how to make [Concerto](https://github.com/campsych/concerto-platform/wiki) and Expfactory coexist and share the same database.

### 1. Edit your post url
Edit the `post_url` variable in [webserver-battery-template.html](templates/webserver-battery-template.html) to change the default URL to the PHP script (`/itest/save_data.php`) if needed. If not a local URL, cross-origin resource sharing should be enabled: refer to [http://enable-cors.org/server_apache.html](http://enable-cors.org/server_apache.html).

### 2. Generate your static files
Then run [setup_battery_for_webserver.py](setup_battery_for_webserver.py) to generate the battery in a specified output folder (likely a web directory)


      python setup_battery_for_webserver.py --output /var/www/vhosts/expfactory-server/digit_span-en --experiments digit_span


### 3. Testing
Though the [run_battery.py](../../script/run_battery.py) script has no use in production, you may test your batteries easily with:


      python run_battery.py --port 8080 /var/www/vhosts/expfactory-server/digit_span-en
