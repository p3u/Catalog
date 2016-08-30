# Arts Catalog
A Flask webserver using SQLite to host a catalog of Arts categorized into art movements.   
A set up for Virtual Machine with Vagrant is included in this repo, so you don't have to install all it's dependencies.  
You can test it's functionality on this [LIVE DEMO](http://pedrosyd.pythonanywhere.com/index/) hosted on pythonanywhere.com.  
This project was a requisite to the [Full Stack Foundations](https://www.udacity.com/course/full-stack-foundations--ud088) course.  


## Requirements
Python 2  
Vagrant  
VirtualBox  

## Initialization
Download this repo to your machine  
Navigate to the Vgrant folder and start your VM  
```
vagrant up
```
Wait for it to start and log in via SSH (On Windows, using Git Bash terminal ensures SSH is included)
```
vagrant ssh
```

To initialize the required tables, navigate to Tournament folder and run:  

To test everything is working, navigate to Catalog and run :  

```
$ python project.py
```

Open your browser and navigate to http://localhost:5000/  

## API Endpoint
The project implements a JSON endpoint that serves the same information as the one displayed in the page index  
You can access it using at http://pedrosyd.pythonanywhere.com/index/JSON or when served locally on http://localhost:5000//index/JSON  

## Technologies used
Python, HTML, CSS, JS  
Flask - Web framework  
SQLite - Database  
SQLalchemy - Object Relational Mapper  
jQuery - For JSON requests  
Jinja2 - Templating  
Google APIs - OAuth 2.0 for Authentication & Authorization  
