#!/usr/bin/env python3
"""
Date created: 2019-05-08
Version: 0.0.1
"""
from datetime import datetime as dt
from datetime import timedelta
from math import pi, acos, sin, cos
from ftplib import FTP, all_errors
import logging
import zipfile
import requests
import os
import json
import pandas as pd


def __create_logger__():
    log = logging.getLogger(__name__)
    p_handler = logging.FileHandler(__name__ + '.txt', 'w')
    p_format = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    p_handler.setFormatter(p_format)
    log.addHandler(p_handler)
    return log


logger = __create_logger__()
logger.setLevel(logging.INFO)

# the resolution dict should help find the resolution
resolution = {'10 min': '10_minutes', '1 min': '1_minute', 'y': 'annual', 'd': 'daily',
              'h': 'hourly', 'm': 'monthly', 'm_y': 'multi_annual', 's_d': 'subdaily'}
reso_folder = {'recent': [500, 1], 'now': [1, 0], 'historical': [14600, 500]}  # days

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
        self.debug_level = 0
        if not os.path.isfile('dwd_tree.txt'):
            self.build_tree()

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

    def build_station_list(self, data: str) -> list:
        """

        :param data:
        :return:
        """
        _dt_format = '%Y%m%d'
        data = data.split('\n')
        data = [' '.join(sta.split(' ')).split() for sta in data]
        del data[1]
        del data[-1]
        data[0].append('Distanz')
        to_delete = list()
        for i in range(1, len(data)):
            if not data[i]:
                to_delete.append(i)
                continue
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

        for delete in to_delete:
            del data[delete]

        return data

    @staticmethod
    def search_folder(key: str, unique: bool = True) -> list:
        """ Search the dwd_tree.txt file for a keyword

        :param key: key word of the folder name
        :type key: str
        :param unique: When the string should be unique
        :type unique: bool
        :return:
        """
        with open('dwd_tree.txt', 'r') as file:
            paths = json.load(file)
        results = list()
        if r'/' in key or r'\\' in key:
            for path in paths:
                    if key in path['path']:
                        results.append(path)
        else:
            for path in paths:
                if unique:
                    if key == path['folder']:
                        results.append(path)
                else:
                    if key in path['folder']:
                        results.append(path)
        return results

    def wind(self, start, end, reso='10_minutes', where='cdc_obDE_climate'):
        """# todo **there some desgin issues**

        :param start: Start-time
        :param end: end-time
        :param reso: Possible values:
        reso = {'10 min': '10_minutes', '1 min': '1_minute', 'y': 'annual',
                'd': 'daily', 'h': 'hourly', 'm': 'monthly', 'm_y': 'multi_annual',
                's_d': 'subdaily'}
        :param where: advance option
        :return:
        """
        if reso in resolution:
            reso = resolution[reso]
        if where == 'cdc_obDE_climate':
            where = self.cdc_obDE_climate
        start, end = self.str_to_timestamp(start, end)
        wind = 'wind'
        wind_paths = self.search_folder(wind)
        for wind_path in wind_paths:
            if reso in wind_path['path'] and where in wind_path['path']:
                path = wind_path['path']
        ftp = self.ftp_login()
        ftp.cwd(path)

        # checks in which directorys the fitting data is (recent, historical, now)
        time_matrix = dict()
        now = dt.now()
        for folder in ftp.nlst():
            time_matrix.update({folder: [False, False]})
            if folder in reso_folder:
                before, after = reso_folder[folder]
                before = now - timedelta(before)
                after = now - timedelta(after)
                if before < start < after:
                    time_matrix[folder][0] = True
                if before < end < after:
                    time_matrix[folder][1] = True
        if 'meta_data' in time_matrix:
            del time_matrix['meta_data']
        if 'now' in time_matrix and 'recent' in time_matrix and 'historical' in time_matrix:
            if time_matrix['historical'][0] and time_matrix['now'][1]:
                time_matrix['recent'] = [True, True]
        stations = dict()
        for key in time_matrix:
            if True in time_matrix[key]:
                ftp.cwd(key)
                for description in ftp.nlst():
                    if 'Beschreibung_Stationen.txt' in description:
                        url = 'https://' + self.server + ftp.pwd() + '/' + description
                        stations.update({key: self.build_station_list(requests.get(url).text)})
                        break
                ftp.cwd('..')

        frames_stations = list()
        for key in stations:
            # list of pd.Dataframe with the stations
            frames_stations.append(pd.DataFrame(stations[key][1:], columns=stations[key][0]).rename_axis(key, axis=1))
        ftp.close()

        tmp_frame = frames_stations[0]
        if len(frames_stations) > 1:
            for x in range(1, len(frames_stations)):
                tmp_frame = pd.merge(tmp_frame, frames_stations[x])
        else:
            frame = tmp_frame

        # todo download the data from every folder
        # todo download the data for a specific station
        # todo merge the data in order 1.) historical, 2.) recent 3.) now
        # todo mark non-consistent data with 'NaN' (like 9999 and so on)
        # todo return the data
        return frame

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
        """Handles the login to the server.
        :return: FTP object
        """
        try:
            ftp = FTP(self.server)
            ftp.set_debuglevel(self.debug_level)
            ftp.login()
            return ftp
        except all_errors as e:
            error_code_string = str(e).split(None, 1)[0]
            print(error_code_string)

    def ftp_set_debuglevel(self, level):
        """Setter for the debugging level of the ftp server

        :param level: Debugging level for teh ftp client
        :return:
        """
        self.debug_level = level

    def ftp_get_data(self, path: str, station_id: str):
        ftp = self.ftp_login()
        ftp.cwd(path)
        file_names = [zip_file for zip_file in ftp.nlst() if station_id in zip_file]
        frames = list()
        for filename in file_names:
            file_type = '.' + filename.split('.')[-1]
            new_filename = 'process/tmp_data' + file_type
            try:
                ftp.retrbinary("RETR " + filename, open(new_filename, 'wb').write)
                with zipfile.ZipFile(new_filename, 'r') as zipObj:
                    # Extract all the contents of zip file in current directory
                    zipObj.extractall('process')
                os.remove(new_filename)
                frame = pd.read_table(os.getcwd() + '\\' + os.listdir()[0], sep=';')
            except:
                print('error')
            frame = frame.replace(-999., 'NaN')
            frame['MESS_DATUM'] = pd.to_datetime(frame['MESS_DATUM'], format='%Y%m%d%H%M')
            frames.append(frame)
        return frames

    def ftp_explore(self, c_ftp, key):
        """**Takes to long, abandon function**

        :param c_ftp:
        :param key:
        :return:
        """
        search_list = list()
        for dire in c_ftp.nlst():
            if '.' in dire:
                pass
            else:
                if key == dire:
                    print(dire)
                    search_list.append(c_ftp.pwd())
                if dire:
                    try:
                        c_ftp.cwd(dire)
                    except all_errors as fail:
                        print(fail)
                        return False
                    search_list.append(self.explore_ftp(c_ftp, key))
                    print(dire)
                    c_ftp.cwd('..')
        return search_list if search_list else None

    def build_tree(self):
        """ Builds a list of dict with the path and a the name of the folder and saves it as a .txt file

        **Example of the .txt**
        First element will be the url

        [
        {"path": "https://opendata.dwd.de", "folder": "https://opendata.dwd.de"},
        {"path": "https://opendata.dwd.de/climate/", "folder": "climate"}
        ]

        :return: True if succeeds
        """
        try:
            url = 'https://' + self.server + '/weather/tree.html'
            tree = requests.get(url).text
            tree = tree[tree.find('<body>') + 6:tree.find('/body') - 7].split('<br>')
        except requests.RequestException as fail:
            print(fail)
            print('Check your internet connection')
            return False
        paths = list()
        i = len(tree) - 1
        ident_start = 'href='
        ident_end = '</a>'
        while i != -1:
            deleted = False
            # delete the element when the key word is not in the string
            if ident_start not in tree[i]:
                del tree[i]
                deleted = True
            if not deleted:
                # find the string and the folder
                slice_start = tree[i].find(ident_start) + len(ident_start) + 1
                slice_end = tree[i].find(ident_end)
                path, folder = tree[i][slice_start:slice_end].split(sep='"')
                path = path.replace('https://opendata.dwd.de/', '')
                paths.append({'path': path, 'folder': folder[1:]})
            i -= 1
        paths.reverse()
        try:
            # save to txt file
            with open('dwd_tree.txt', 'w') as f:
                json.dump(paths, f)
        except IOError as fail:
            print(fail)
            print('Saving the dwd_tree.txt was not successful')
            return False
        return True

    @staticmethod
    def str_to_timestamp(start: str, end: str):
        """Returns a datetime object

        :param start: ISO Format timestamp string with 'T' as separator
        :param end: ISO Format timestamp string with 'T' as separator

        **Example:**
        Date of the example: 2018-03-02
        str_to_timestamp('2000-12-31T10:24', '2000-12-31T11:24'))

        :returns: (datetime, datetime)
        """
        dati_form = {'time': {2: '%H', 4: '%H%M', 6: '%H%M%S'},
                     'date': {6: '%y%m%d', 8: '%Y%m%d'}
                     }

        def is_numeric(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        def drop_char(string):
            tmp = ''
            for c in string:
                if is_numeric(c):
                    tmp = tmp + c
            return tmp

        start = start.replace(' ', 'T')
        end = end.replace(' ', 'T')
        length = len(start)
        try:
            if length != len(end):
                print('Start and end date are not in the same format')
                raise SyntaxError
            if ('T' not in start or 'T' not in end) and length > 10:
                print('There have to be a "T" or a space between the date and the time')
                raise SyntaxError
        except SyntaxError as fail:
            print(fail)
            print('There are several formats supported, please use one of them.')
            print(dati_form)
            return None
        try:
            if 'T' in start:
                date, time = start.split('T')
                time = drop_char(time)
                time_format = dati_form['time'][len(time)]
            else:
                date = start
                time_format = ''
            date = drop_char(date)
            date_format = dati_form['date'][len(date)]
            datetime_format = date_format + time_format

            start = drop_char(start)
            end = drop_char(end)

            timestamp_start = dt.strptime(start, datetime_format)
            timestamp_end = dt.strptime(end, datetime_format)
        except KeyError:
            print("Check your timestamps. Here an Example: '2019-01/01T00', '2019/02$01T00'")
            return None

        if timestamp_start > timestamp_end:
            timestamp_start = timestamp_end
            timestamp_end = dt.strptime(start, datetime_format)

        return timestamp_start, timestamp_end

test_path = r'opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/wind/historical/'
loca = Location(53.494361, 11.445833)
#data = loca.ftp_get_data(test_path, '04625')
#print(data)