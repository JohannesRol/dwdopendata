#!/usr/bin/env python3
"""
Date created: 2019-05-08
Version: 0.0.1
"""
from ftplib import FTP
from datetime import datetime as dt
from math import pi, acos, sin, cos

_dt_format = '%Y%m%d'
# the resolution dict should help find the resolution
resolution = {'10 min': '10_minutes', '1 min': '1_minute', 'y': 'annual', 'd': 'daily',
              'h': 'hourly', 'm': 'monthly', 'm_y': 'multi_annual', 's_d':'subdaily'}

class Location:
    """The Location object builds a list of the stations listed on the dwd server sorted by the distance
    """
    def __init__(self, lat: float=51.0, lon: float=10):
        """
        :param lon: longitude (example 51.0)
        :param lat: latitude (example 10.0)
        """
        self.coordinate = [lat, lon]

    def calc_distance(self, station: list) -> float:
        """Builds the distance between the given point and the station
        :param station: coordinates of the station
        :return: the distance
        """
        lat1, lon1 = [co * pi / 180 for co in self.coordinate]
        lat2, lon2 = [co_st * pi / 180 for co_st in station]
        radius = 6378.388  # * pi / 180  # = 111.324
        return radius * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon2 - lon1))

    def build_station_list(self, data: list) -> list:
        data = [' '.join(sta.split(' ')).split() for sta in data]
        del data[1]
        data[0].append('Distanz')
        for i in range(1, len(data)):
            if len(data[i]) != len(data[0]) - 1:
                data[i] = data[i][0:6] + [' '.join(data[i][6:-1]), data[i][-1]]
            data[i][1] = dt.strptime(data[i][1], _dt_format)
            data[i][2] = dt.strptime(data[i][2], _dt_format)
            data[i][3] = float(data[i][3])
            data[i][4] = float(data[i][4])
            data[i][5] = float(data[i][5])
            # calc the distance
            data[i].append(self.calc_distance(data[i][4:6]))
        data[1:-1] = sorted(data[1:-1], key=lambda x: x[-1])

        return data

    def wind(self, reso='10_mintues'):
        if reso in resolution:
            reso = resolution[reso]
        wind = 'wind'
        print(reso + '/' + wind)
        path = 'TEST_station.txt'
        with open(path, 'r') as file:
            data = file.readlines()
        file.close()
        del path, file
        stations = self.build_station_list(data)
        return stations

    def solar(self, reso='10_Minutes'):
        if reso in resolution:
            reso = resolution[reso]
        solar = 'solar'
        print(reso + '/' + solar)
        path = 'TEST_station.txt'
        with open(path, 'r') as file:
            data = file.readlines()
        file.close()
        del path, file
        stations = self.build_station_list(data)
        return stations
