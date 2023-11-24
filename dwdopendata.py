#!/usr/bin/env python3
"""
Date created: 2019-05-08
Version: 0.0.1
"""
from datetime import datetime as dt
from datetime import timedelta
from math import pi, acos, sin, cos, log
from ftplib import FTP, all_errors
import requests
import os
import json
import pandas as pd
import numpy as np

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
        """Returns a string in a specific format.

        :return: String with "Latitude: %s, Longitude: %s"
        """
        return 'Latitude: ' + str(self.coordinate[0]) + ', Longitude: ' + str(self.coordinate[1])

    def calc_distance(self, lat_lon) -> float:
        """Calculates the distance between the given point and the station

        :param lat_lon: coordinates of the station in a list [LAT, LON]
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
                if key == path['path']:
                    return path
        else:
            for path in paths:
                if unique:
                    if key == path['folder']:
                        results.append(path)
                else:
                    if key in path['folder']:
                        results.append(path)
        return results

    def wind(self, start, end, station_id=None, folder='cdc_obDE_climate'):
        """Downloads wind-data from the nearest station

        :param start: Start-time
        :param end: end-time
        :param reso: Possible values:
            reso = {'10 min': '10_minutes', 'h': 'hourly', 's_d': 'subdaily'}
        :param station_id: ID of the station
        :param folder: test / advance option
        :return:
        """
        return self.get_10_min_data(start, end, 'wind', station_id, folder)

    def temperature(self, start, end, station_id=None, folder='cdc_obDE_climate'):
        return self.get_10_min_data(start, end, 'air_temperature', station_id, folder)

    def precipitation(self, start, end, station_id=None, folder='cdc_obDE_climate'):

        return 'not ready jet'
        # return self.get_10_min_data(start, end, 'precipitation', station_id, folder)

    def solar(self, start, end, station_id=None, folder='cdc_obDE_climate'):
        """Downloads wind-data from the nearest station

        :param start: Start-time
        :param end: end-time
        :param reso: Possible values:
            reso = {'10 min': '10_minutes', 'h': 'hourly', 's_d': 'subdaily'}
        :param station_id: ID of the station
        :param folder: test / advance option
        :return:
        """
        return self.get_10_min_data(start, end, 'solar', station_id, folder)

    def get_10_min_data(self, start, end, typ, station_id=None, folder='cdc_obDE_climate'):
        reso = '10_minutes'
        if folder == 'cdc_obDE_climate':
            folder = self.cdc_obDE_climate
        start, end = self.str_to_timestamp(start, end)
        path = folder + reso + f'/{typ}/'
        path = self.search_folder(path)['path']
        ftp = self.ftp_login()
        ftp.cwd(path)

        time_matrix = self.timematrix(ftp.nlst(), start, end)

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

        # download data from every folder
        time_column = 'MESS_DATUM'
        data = dict()

        for station in stations:
            # print(station.head().to_string())
            key = station.columns.name
            current_folder = folder_name + key
            if station[station.isin([station_id])].empty:
                print('Station ID is not in the list, set station ID to the nearest station')
                station_id = None
            station_id = station_id or station['Stations_id'].iloc[0]
            tmp_frame = pd.concat(self.ftp_get_data(current_folder, station_id, start, end))
            tmp_frame.set_index(time_column, inplace=True)
            stiation_height = station.loc[station['Stations_id'] == station_id, 'Stationshoehe'].iloc[0]
            tmp_frame.columns.set_names('Height [m]: ' + stiation_height, inplace=True)
            data.update({key: tmp_frame})

        # Concat frames in the order 1.) historical 2.) recent 3.) now
        frame = None
        if len(data) == 1:
            frame = data[list(data.keys())[0]]
        else:
            if 'historical' in data.keys():
                frame = data.pop('historical')
            elif 'recent' in data.keys():
                frame = frame.pop('recent')
            elif 'now' in data.keys():
                frame = data.pop('now')

            if frame is not None:
                if 'recent' in data.keys():
                    tmp_frame = data.pop('recent')
                    tmp_frame = tmp_frame[(tmp_frame.index < frame.last_valid_index())]
                    frame = pd.concat([frame, tmp_frame])
                if 'now' in data.keys():
                    tmp_frame = data.pop('now')
                    tmp_frame = tmp_frame[(tmp_frame.index < frame.last_valid_index())]
                    frame = pd.concat([frame, tmp_frame])

        frame = frame[(frame.index >= start) & (frame.index < end)]
        frame = frame.loc[~frame.index.duplicated(keep='first')].sort_index()
        frame = frame.drop('eor', axis=1)
        if reso == '10_minutes':
            frame = frame.asfreq('10T')

        return {'data': frame, 'meta': stations}

    def ftp_login(self, debug_level=None):
        """Handles the login to the server.
        :param debug_level: debug level of the ftp logging
        :return: FTP object
        """
        if debug_level:
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
        :param sep: separator between the words
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

    def recalc_height(self, frame, h2: float, h1: float = None, factor: float = 0.14,
                      method: str = 'hellmann', column: str = 'FF_10', inplace=False):

        if not inplace:
            frame = frame.copy()
        h1 = h1 or float(frame.columns.name.split(' ')[-1])
        if method.lower() == 'hellmann':
            frame[column] = frame[column].apply(self.elevation_profil_hellmann, args=(h1, h2, factor))
        else:
            frame[column] = frame[column].apply(self.log_windprofil, args=(h1, h2, factor))
        frame.columns.set_names('Height [m]: ' + str(h2), inplace=True)
        if not inplace:
            return frame[column]

    @staticmethod
    def timematrix(folder_list, start, end):
        # checks in which directory the fitting data is (recent, historical, now)
        time_matrix = dict()
        now = dt.now()
        for folder in folder_list:
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
        return time_matrix

    @staticmethod
    def read_data(path: str):
        """Read data from a txt file in the process directory or from the given path.

        :param path: path where the data is stored
        :return: frames of the data
        """
        filename = path.replace('\\', '/').replace('.', '/')
        filename = filename.split('/')[-2]

        time_format = '%Y%m%d%H%M'
        time_column = 'MESS_DATUM'
        frame = pd.read_table(path, sep=';')
        frame = frame.replace(-999., np.nan)
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

        if timestamp_start > timestamp_end:
            timestamp_start = timestamp_end
            timestamp_end = dt.strptime(start, datetime_format)

        return timestamp_start, timestamp_end

    @staticmethod
    def elevation_profil_hellmann(v1, h1, h2, alpha):
        """Extrapolation of wind speed in a different height

        With the help of the power law according to Hellmann, the approximately wind speed can be determined at
        any height based on a measured wind speed at a certain height.

        **Example**
        df.FF_10 = df.FF_10.apply(elevation_profil_hellmann, args=(10,100,0.14))

        :param v1: Wind speed
        :param h1: height of the station
        :param h2: the new height
        :param alpha: exponent of the heights
        :return: extrapolation of new the wind speed
        """
        return v1 * (h2/h1)**alpha

    @staticmethod
    def log_windprofil(v1, h1, h2, z_0):
        """Extrapolation of the wind speed in a different height

        With the help of the logarithmic wind profil, the approximately wind speed can be determined at any height
         based on a measured wind speed at a certain height.

        **Example**
        df.FF_10 = df.FF_10.apply(log_windprofil, args=(10,100,0.14))

        :param v1: wind speed
        :param h1: height of the station
        :param h2: the new height
        :param z_0: Roughness length of the enviroment
        :return: extrapolation of the new wind speed
        """
        return v1 * log(h2/z_0)/log(h1/z_0)


def resample_data(data, freq='60min'):
    """ Resamples the given pd.DataFrame in data['data'] with the resample function.
    for people how are to lazy to think each time they resample the return from the functions above

    :param data: Feedback from for example Location.wind(...) or .solar()
    :param freq: default 60 min. For more see pd.DataFrame.resample(...) function
    """
    id = data['data'].STATIONS_ID[0]
    data['data'].drop([qn for qn in data['data'].columns if 'QN' in qn][0], axis=1, inplace=True)
    data['data'] = data['data'].resample(freq, label='right').sum()
    data['data'].STATIONS_ID = id
    return data


def j_cm2_to_wh_m2(data):
    """Calculates the pd.DataFrame() from the Location.solar(...) feedback
     from joule per qubic centimeter to watt hour per squarer meter.
    """
    data['data'].DS_10 = data['data'].DS_10 / .36
    data['data'].GS_10 = data['data'].GS_10 / .36
    return data


if __name__ == "__main__":
    loca = Location()
    loca.wind('2011-01-01T00:00', '2019-07-06T00:00')
