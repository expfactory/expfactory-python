FROM python:2.7

RUN apt-get update && apt-get -y install vim

RUN mkdir /code
ADD . /code

RUN /bin/sh /code/variables.sh

# install the dependencies from the package.json file
RUN pip install expfactory

# make port 80 available outside of the image
EXPOSE 80

# Start with the script to install experiments
WORKDIR /code


docker run \
--detach \
--name=expfactory-mysql \
--env="MYSQL_ROOT_PASSWORD=composer" \
--publish 6603:3306 \
--volume=./conf.d:/etc/mysql/conf.d \
--volume=./data:/var/lib/mysql \
mysql

