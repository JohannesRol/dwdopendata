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
    def __init__(self, lat: float = 51.0, lon: float = 10.0, op_path: str = None):
        """
        :param lon: longitude (example 51.0)
        :param lat: latitude (example 10.0)
        """
        self.coordinate = [lat, lon]
        self.server = 'opendata.dwd.de'
        self.cdc_obDE_climate = 'climate_environment/CDC/observations_germany/climate/'
        self.debug_level = 0
        self.op_path = os.getcwd() or op_path
        if not os.path.isfile(self.op_path + '\\dwd_tree.txt'):
            self.build_tree()

    def __str__(self):
        """Returns a string in a specific format

        :return: String with "Latitude: %s, Longitude: %s"
        """
        return 'Latitude: ' + str(self.coordinate[0]) + ', Longitude: ' + str(self.coordinate[1])

    def calc_distance(self, lat_lon) -> float:
        """Calculates the distance between the given point and the station

        :param station: coordinates of the station in a list [LAT, LON]
        :return: the distance between the two points
        :rtype: float
        """
        lat1, lon1 = [float(co) * pi / 180 for co in self.coordinate]
        lat2, lon2 = [float(co_st) * pi / 180 for co_st in lat_lon]
        radius = 6378.388  # * pi / 180  # = 111.324
        return radius * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon2 - lon1))

    def station_list(self, url: str):
        """ Builds a pandas Dataframe of the stations from the given url sorted by the distance from the coordinates

        :param url: URL to the station list
        :type url: str
        :return: pd.DataFrame of the station sorted by the distance from the location
        :rtype: pd.DataFrame
        """
        _dt_format = '%Y%m%d'
        stations = [text.split() for text in requests.get(url).text.split('\r\n')]
        sta = list()
        for station in stations[2:]:
            if len(station) > 7:
                tmp = station[:6]  # first 6 data point
                tmp.append(' '.join(map(str, station[6:-1])))  # location
                tmp.append(station[-1])  # german federal state
                sta.append(tmp)
        col_name = stations[0]
        sta = pd.DataFrame(sta, columns=col_name)
        sta[col_name[1]] = pd.to_datetime(sta[col_name[1]], format=_dt_format)
        sta[col_name[2]] = pd.to_datetime(sta[col_name[2]], format=_dt_format)
        sta['distanz'] = sta[['geoBreite', 'geoLaenge']].apply(self.calc_distance, axis=1)
        sta = sta.sort_values(by='distanz')
        return sta

    def search_folder(self, key: str, unique: bool = True) -> list:
        """ Search the dwd_tree.txt file for a keyword

        :param key: key word of the folder name
        :type key: str
        :param unique: When the string should be unique
        :type unique: bool
        :return: dictionary with path to the folder
        """
        dwd_tree_path = self.op_path + '\\dwd_tree.txt'
        with open(dwd_tree_path, 'r') as file:
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
        stations = list()
        for key in time_matrix:
            if True in time_matrix[key]:
                ftp.cwd(key)
                for description in ftp.nlst():
                    if 'Beschreibung_Stationen.txt' in description:
                        url = 'https://' + self.server + ftp.pwd() + '/' + description
                        stations.append(self.station_list(url).rename_axis(key, axis=1))
                        break
                ftp.cwd('..')
        folder_name = ftp.pwd() + '/'
        ftp.close()

        data = list()
        for station in stations:
            current_folder = folder_name + station.columns.name
            station_id = station['Stations_id'].iloc[0]
            data.append(self.ftp_get_data(current_folder, station_id, start, end))
            # todo download the data from every folder

        # todo download the data from every folder
        # todo download the data for a specific station
        # todo merge the data in order 1.) historical, 2.) recent 3.) now
        # todo mark non-consistent data with 'NaN' (like 9999 and so on)
        # todo return the data
        return data

    def solar(self, reso: str = '10_Minutes'):
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

    def ftp_login(self, debug_level):
        """Handles the login to the server.
        :param debug_level: debug level of the ftp logging
        :return: FTP object
        """
        self.debug_level = debug_level
        try:
            ftp = FTP(self.server)
            ftp.set_debuglevel(self.debug_level)
            ftp.login()
            return ftp
        except all_errors as e:
            error_code_string = str(e).split(None, 1)[0]
            print(error_code_string)

    def ftp_get_data(self, path: str, station_id: str, start: str = None, end: str = None):
        """Gets the data from the dwd server and returns it as pd.DataFrame

        :param path: path to the directory were the data is stored
        :param station_id: ID of the station
        :param start: Starttime (only for historical data)
        :param end: Endtime ( only for historical data)
        :return: pd.DataFrame
        """

        ftp = self.ftp_login()
        ftp.cwd(path)
        file_names = [zip_file for zip_file in ftp.nlst() if station_id in zip_file]
        ftp.quit()
        if 'historical' in path:
            if start is not None and end is not None:
                file_names = self.filter_list_of_directory_by_time(file_names, start, end)

        frames = list()
        for filename in file_names:
            frames.append(self.read_data('ftp://' + self.server + path + '/' + filename))
        return frames

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
            with open(self.op_path + '\\dwd_tree.txt', 'w') as f:
                json.dump(paths, f)
        except IOError as fail:
            print(fail)
            print('Saving the dwd_tree.txt was not successful')
            return False
        return True

    def filter_list_of_directory_by_time(self, metadata: list, start: str, end: str, sep: str = '_'):
        """Filters the given list of strings by time. The 5th and 6th element must be a date string.

        :param metadata: List of zip file names
        :param start: start time of the time frame
        :param end: end time of the time frame
        :param sep: seperator between the words
        :return: list with the zip file and the right time frame
        """
        if type(start) == type(end) and start is None:
            return metadata
        if isinstance(start, str) or isinstance(end, str):
            start, end = self.str_to_timestamp(start, end)

        output = list()
        for i in range(len(metadata)):
            meta = metadata[i].split(sep)
            meta_start, meta_end = self.str_to_timestamp(meta[3], meta[4])
            if start <= meta_start <= end or start <= meta_end <= end or meta_start <= end <= meta_end:
                output.append(metadata[i])

        return output if output.__len__() > 0 else metadata

    @staticmethod
    def read_data(path: str):
        """Read data from the txt file in the process directory or from the given path.

        :param station_id: If station ID is given, returns only frames of the station in the process directory
        :param path: path where the data is stored
        :param remove_files: remove the files after extrating the data
        :return: frames of the the data
        """
        filename = path.replace('\\', '/').replace('.', '/')
        filename = filename.split('/')[-2]

        time_format = '%Y%m%d%H%M'
        time_column = 'MESS_DATUM'
        frame = pd.read_table(path, sep=';')
        frame = frame.replace(-999., pd.np.nan)
        frame[time_column] = pd.to_datetime(frame[time_column], format=time_format)
        frame.rename_axis(filename, axis=1)
        return frame

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
                raise ValueError
            if ('T' not in start or 'T' not in end) and length > 8:
                print('There have to be a "T" or a space between the date and the time')
                raise ValueError
        except ValueError as fail:
            print(fail)
            print('There are several formats supported, please use one of them.')
            print(dati_form)
            raise ValueError
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
            raise KeyError
            return None

        if timestamp_start > timestamp_end:
            timestamp_start = timestamp_end
            timestamp_end = dt.strptime(start, datetime_format)

        return timestamp_start, timestamp_end
