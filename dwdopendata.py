#!/usr/bin/env python3
"""
Date created: 2019-05-08
Version: 0.0.1
"""
from datetime import datetime as dt
from math import pi, acos, sin, cos
from ftplib import FTP, all_errors
import zipfile


# the resolution dict should help find the resolution
resolution = {'10 min': '10_minutes', '1 min': '1_minute', 'y': 'annual', 'd': 'daily',
              'h': 'hourly', 'm': 'monthly', 'm_y': 'multi_annual', 's_d': 'subdaily'}


class Location:
    """The Location object builds a list of the stations listed on the dwd server sorted by the distance
    """
    def __init__(self, lat: float = 51.0, lon: float = 10.0):
        """
        :param lon: longitude (example 51.0)
        :param lat: latitude (example 10.0)
        """
        self.coordinate = [lat, lon]
        self.server = 'opendata.dwd.de'
        self.cdc_obDE_climate = 'climate_environment/CDC/observations_germany/climate/'

    def __str__(self):
        return 'Latitude: ' + str(self.coordinate[0]) + ', Longitude: ' + str(self.coordinate[1])

    def calc_distance(self, station: list) -> float:
        """Builds the distance between the given point and the station
        :rtype: float
        :param station: coordinates of the station
        :return: the distance
        """
        lat1, lon1 = [co * pi / 180 for co in self.coordinate]
        lat2, lon2 = [co_st * pi / 180 for co_st in station]
        radius = 6378.388  # * pi / 180  # = 111.324
        return radius * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon2 - lon1))

    def build_station_list(self, data: list) -> list:
        _dt_format = '%Y%m%d'
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

    def wind(self, timestamp_start, timestamp_end, reso='10_minutes'):
        if reso in resolution:
            reso = resolution[reso]
        wind = 'wind'
        path = self.cdc_obDE_climate + reso + '/' + wind
        print(path)
        return path
        # with open(path, 'r') as file:
        #    data = file.readlines()
        # file.close()
        # stations = self.build_station_list(data)
        # return stations

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

    def ftp_login(self):
        try:
            ftp = FTP(self.server)
            ftp.login()
        except all_errors as e:
            error_code_string = str(e).split(None, 1)[0]
            print(error_code_string)
        return ftp

    def explore_ftp(self, c_ftp, key):
        search_list = list()
        for dire in c_ftp.nlst():
            if '.' in dire:
                pass
            else:
                if key in dire:
                    print(dire)
                    search_list.append(c_ftp.pwd())
                    return search_list
                if dire:
                    c_ftp.cwd(dire)
                    search_list.append(self.explore_ftp(c_ftp, key))
                    print(dire)
                    c_ftp.cwd('..')
        return search_list


def unzip():
    _dt_format = '%Y%m%d%H%M'
    ipath = '/Users/Johnny/Documents/repo/dwdopendata/10minutenwerte_ff_00003_19930428_19991231_hist.zip'
    with zipfile.ZipFile(ipath, "r") as zip_ref:
        with zip_ref.open(zip_ref.namelist()[0], 'r') as myfile:
            data = myfile.readlines()
    data = [data_point.decode().strip().split(';') for data_point in data]
    for i in range(1, len(data)):
        data[i][0] = data[i][0].strip()
        data[i][1] = dt.strptime(data[i][1].strip(), _dt_format)
        data[i][2] = float(data[i][2].strip())
        data[i][3] = float(data[i][3].strip())
        data[i][4] = float(data[i][4].strip())
    return data
