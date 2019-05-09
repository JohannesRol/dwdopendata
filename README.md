# DWDopendata

## Description
The package should help you to integrate the data from opendata dwd into python

https://opendata.dwd.de/

An alternative to this project is the dwd-weather package.

https://github.com/marians/dwd-weather

## Installation
python3 -m pip install dwdopendata

## Usage
```
import dwdopendata as dwd
# set your location
location = dwd.location(51.898, 8.9876)
# gives back the wind speed
wind_speed = location.wind(2019-05-01T00:00:00, 2019-05-02T00:00:00, '10min')
```

# Support
stackoverflow, tag => dwdopendata 


# Roadmap
first I want to focus on ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/
* code the basic framework
* add functions
* refactor it
* do fancy stuff

# Contributing
It's in a bloody early state. I'm grateful for any who wants to help.



# Authors and acknowledgment


# License
Licensed under the MIT license. See file LICENSE for details.

# Copyright (data)
terms of use: https://www.dwd.de/copyright

# Project status

V00.00: there is nothing

# todo
build a coordinates function that gives back an station object
