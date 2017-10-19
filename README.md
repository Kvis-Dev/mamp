# mamp

Mac

~~Apache~~ nginx :)

MySQL

PHP

## intro
This set of scripts is written to manage webserver on mac. It was inspired by denwer and openserver.
I want to create a set of scripts that woud do all the dirty job for you, because setting it all up is really annoying.

## features
 - Uses brew to manage packages, so the size of this scripts is not very big.

## requirements
 - Python 3
 - [brew](https://brew.sh/)


## installation
Just clone this repository anywhere you want.

## usage

`sudo python3 main.py [start|stop|status|restart|wizard]`


 * `sudo python3 main.py start` - starts all the services
 * `sudo python3 main.py stop` - stops all the services
 * `sudo python3 main.py status` - prints the status of all services
 * `sudo python3 main.py restart` - restarts all the services
 * `sudo python3 main.py wizard` - starts a wizard that helps you create a local domain. You just answer a few questions and voila! all done!


tags: mamp, free mamp, brew, nginx, web server
