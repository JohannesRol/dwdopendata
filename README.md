#DWDopendata
###Description
Works for historical wind and solar data

###Usage
```
import dwdopendata as dwd
import date_picker as dp
# set your location
location = dwd.Location(48.37, 10.94)
# timestamps from last month
ts = dp.last_month_ts()
# gives back the wind speed
wind_speed = location.wind(ts.start(), ts.end())  # yaaii Wind speed data
solar = location.solar(ts.start(), ts.end())  # yaaii solar data

#  some other functions for solar
solar = dwd.resample_data(solar,'m')
solar = dwd.j_cm2_to_wh_m2(solar)

# usage example: Nominal return (=> performance ratio) for a solar power plant
module_area = 3731  # sqaure meters
module_efficiency = 20.15  # %
Nominal_return = solar['data'].GS_10 * module_area * module_efficiency / 1000
# performance_ratio = yield / Nominal_return
```

###Support
issue section

###Roadmap
ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/

###License
Licensed under the MIT license. See file LICENSE for details.

###Copyright (data)
terms of use: https://www.dwd.de/copyright

###Project status
V0.98

###todo
