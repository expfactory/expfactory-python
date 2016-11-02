# Expfactory Server (SQL)

This will provide a static (SQL) server setup, that can either be run on a server natively (locally), or with a MySQL Dockerized database. Instructions for composer are included below:

- Integration with [Composer]():

The instructions for the Dockerized database are included here.

## Customizing your SQL Server
This is primarily intended for development, and if you would like a complete Dockerized application we recommend either using expfactory-docker or submitting a PR to this repo.  The following command, run from this directory, will set up a mysql database available on port 3306 called `expfactory-mysql`

	docker run \
	--detach \
	--name=expfactory-mysql \
	--env="MYSQL_ROOT_PASSWORD=composer" \
	--publish 6603:3306 \
	--volume=conf.d:/etc/mysql/conf.d \
	--volume=data:/var/lib/mysql \
	mysql

You can also set one up at the server of your choice. If you use the setup provided above, continue. Otherwise, be sure to change the host/etc credentials in `create_expfactory_table.php` and `database_conncect.php`.


