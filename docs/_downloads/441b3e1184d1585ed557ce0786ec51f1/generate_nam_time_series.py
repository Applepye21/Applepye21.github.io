import os
import numpy as np
import datetime
import sys
import extract_nam_data
import region_data
sys.path.insert(1, '/uufs/chpc.utah.edu/common/home/zpu-group25/mpye/base_scripts')
import my_stats
import save_files


#Creates an object that contains 6-hourly time series of a given NAM data
#variable in a certain specified region of the NAM domain. It also contains a
#list of times the data represents. Time periods within the desired text_file 
#can also be converted into an object by entering string dates into the 
#start_date and end_date parameters in the format YYYY-MM-DD. You can also use
#the first or last portion of the data by entering a new value for either 
#start_date or end_date, you do not need to enter a value for both.
class nam_time_series(object):
    def __init__(self, txt_file_path, start_date = '10-01', end_date = '09-30'):
        start_date_created = False
        end_date_created = False
        if start_date == '10-01':
            start_date = datetime.datetime.strptime(str(int(txt_file_path.split('/')[-1][:4]) - 1) + '-' + start_date, '%Y-%m-%d')
            start_date_created = True
        if end_date == '09-30':
            end_date = datetime.datetime.strptime(txt_file_path.split('/')[-1][:4] + '-' + end_date, '%Y-%m-%d')
            end_date_created = True
        if start_date_created == False:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        if end_date_created == False:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        file = open(txt_file_path, 'r')
        self.dates = []
        self.times = []
        self.values = []
        for line in file:
            if line[0] != '#':
                date, time, value = line.split(', ')
                current_date_object = datetime.datetime.strptime(date, '%Y-%m-%d')
                if start_date <= current_date_object <= end_date:  
                    self.dates.append(date)
                    self.times.append(time)
                    self.values.append(float(value))
        current_date = self.dates[0]
        self.daily_dates = [current_date]
        for date in self.dates:
            if date != current_date:
                self.daily_dates.append(date)
            current_date = date

    #Changes the "values" attribute to contain average daily values and associated
    #dates based on the 6-hourly data.
    def daily_time_series(self):
        daily_values = []
        day_values = []
        for date, time, value in zip(self.dates, self.times, self.values):
            day_values.append(value)
            if time == '18':
                daily_values.append(my_stats.mean(day_values))
                day_values = []
        self.values = daily_values
        self.ready_for_multiple_day = True
        return self

    #Changes the "values" attribute to a time series for just a particular hour 
    #of the day. For exampleif just the morning value from each day is desired,  
    #enter "'12'" (thisshould be entered as a string with padded zeroes). This 
    #will return a listof all values of the variable at 12Z for the entire time  
    #period. The possible options for the hour parameter are '00', '06', '12', 
    #and '18'.
    def hour_time_series(self, hour):
        hour_series = []
        for time, value in zip(self.times, self.values):
            if time == hour:
                hour_series.append(value)
        self.values = hour_series
        self.ready_for_multiple_day = True
        return self

    #Changes the "values" attribute to contain a time series of multiple day 
    #averages. It also changes the "daily_dates" attribute to represent the 
    #same dates as the new time series dates based. The number of days to  
    #average must be an odd integer and is set to a default of 7. Before
    #using this method, "daily_time_series" or "hour_time_series" must be
    #used first.
    def multiple_day_average_time_series(self, num_of_days = 7):
        if num_of_days % 2 == 0:
            raise ValueError('The variable "num_of_days" must be an odd integer, please reset the value')
        if hasattr(self, 'ready_for_multiple_day') == False:
            raise UnboundLocalError('Raw data set must be converted to an hour_time_series() or a daily_time_series() before being converted to a multiple_day_average_time_series()')
        averaged_time_series = my_stats.multiple_day_average(self.values, num_of_days)
        start_index = int((num_of_days - 1) / 2)
        end_index = start_index * -1
        self.daily_dates = self.daily_dates[start_index:end_index]
        self.values = averaged_time_series
        return self

    #Returns a list of datetime objects based on the string dates found in
    #the "dates" attribute
    def dates_datetime_objects(self):
        return [datetime.datetime.strptime(date, '%Y-%m-%d') for date in self.dates]

    #Returns a list of datetime objects based on the string dates found in
    #the "dates" attribute
    def datetimes_datetime_objects(self):
        return [datetime.datetime.strptime(date + ' ' + time, '%Y-%m-%d %H') for date, time in zip(self.dates, self.times)]

    #Returns a list of datetime objects based on the string dates found in
    #the "daily_dates" attribute
    def daily_dates_datetime_objects(self):
        return [datetime.datetime.strptime(date, '%Y-%m-%d') for date in self.daily_dates]


#Creates an object that contains 6-hourly time series of "drought" (2021-2022)
#minus "non-drought" (2018-2019) conditions of a given NAM data variable in a 
#certain specified region of the NAM domain. It also contains a list of times
#the data represents. Time periods within the desired text_file can also be 
#converted into an object by entering string dates into the start_date and 
#end_date parameters in the format YYYY-MM-DD. You can also use the first or
#last portion of the data by entering a new value for either start_date or 
#end_date, you do not need to enter a value for both.
class drought_minus_non_drought_time_series(object):
    def __init__(self, var_dir, region_name, drought_start_date = '2020-10-01', drought_end_date = '2022-09-30'):
        start_date_created = False
        end_date_created = False
        drought_start_month_day= drought_start_date[5:]
        drought_end_month_day = drought_end_date[5:]
        if drought_start_date == '2020-10-01':
            drought_start_date = datetime.datetime.strptime(drought_start_date, '%Y-%m-%d')
            start_date_created = True
        if drought_end_date == '2022-09-30':
            drought_end_date = datetime.datetime.strptime(drought_end_date, '%Y-%m-%d')
            end_date_created = True
        if start_date_created == False:
            drought_start_date = datetime.datetime.strptime(drought_start_date, '%Y-%m-%d')
        if end_date_created == False:
            drought_end_date = datetime.datetime.strptime(drought_end_date, '%Y-%m-%d')

        txt_file_path = '/uufs/chpc.utah.edu/common/home/zpu-group25/mpye/nam_analysis_data/variable_time_series/' + var_dir + '/txt_files'
        all_file_list = os.listdir(txt_file_path)
        region_file_list = []
        for file_name in all_file_list:
            if region_name in file_name:
                region_file_list.append(txt_file_path + '/' + file_name)
        file_2018, file_2019, file_2021, file_2022 = sorted(region_file_list)

        self.dates = []
        self.times = []
        self.values = []
        if drought_start_date < datetime.datetime(2021, 10, 1):
            data_2018 = nam_time_series(file_2018, '2017-' + drought_start_month_day, '2018-' + drought_end_month_day)
            data_2021 = nam_time_series(file_2021, '2020-' + drought_start_month_day, '2021-' + drought_end_month_day)
            self.dates += data_2021.dates
            self.times += data_2021.times
            self.values = list(np.array(data_2021.values) - np.array(data_2018.values))
        if drought_end_date >= datetime.datetime(2021, 10, 1):
            data_2019 = nam_time_series(file_2019, '2018-' + drought_start_month_day, '2019-' + drought_end_month_day)
            data_2022 = nam_time_series(file_2022, '2021-' + drought_start_month_day, '2022-' + drought_end_month_day)
            self.dates += data_2022.dates
            self.times += data_2022.times
            self.values = list(np.array(data_2022.values) - np.array(data_2019.values))

        current_date = self.dates[0]
        self.daily_dates = [current_date]
        for date in self.dates:
            if date != current_date:
                self.daily_dates.append(date)
            current_date = date

    #Changes the "values" attribute to contain average daily values and associated
    #dates based on the 6-hourly data.
    def daily_time_series(self):
        daily_values = []
        day_values = []
        for date, time, value in zip(self.dates, self.times, self.values):
            day_values.append(value)
            if time == '18':
                daily_values.append(my_stats.mean(day_values))
                day_values = []
        self.values = daily_values
        return self

    #Changes the "values" attribute to a time series for just a particular hour 
    #of the day. For exampleif just the morning value from each day is desired,  
    #enter "'12'" (thisshould be entered as a string with padded zeroes). This 
    #will return a listof all values of the variable at 12Z for the entire time  
    #period. Thepossible options for the hour parameter are '00', '06', '12', 
    #and '18'.
    def hour_time_series(self, hour):
        hour_series = []
        for time, value in zip(self.times, self.values):
            if time == hour:
                hour_series.append(value)
        self.values = hour_series
        return self

    #Changes the "values" attribute to contain a time series of multiple day 
    #averages. It also changes the "daily_dates" attribute to represent the 
    #same dates as the new time series dates based. The number of days to  
    #average must be an odd integer and is set to a default of 7. Before
    #using this method, "daily_time_series" or "hour_time_series" must be
    #used first.
    def multiple_day_average_time_series(self, num_of_days = 7):
        if num_of_days % 2 == 0:
            raise ValueError('The variable "num_of_days" must be an odd integer, please reset the value')
        averaged_time_series = my_stats.multiple_day_average(self.values, num_of_days)
        start_index = int((num_of_days - 1) / 2)
        end_index = start_index * -1
        self.daily_dates = self.daily_dates[start_index:end_index]
        self.values = averaged_time_series
        return self

    #Returns a list of datetime objects based on the string dates found in
    #the "dates" attribute
    def dates_datetime_objects(self):
        return [datetime.datetime.strptime(date, '%Y-%m-%d') for date in self.dates]

    #Returns a list of datetime objects based on the string dates found in
    #the "daily_dates" attribute
    def daily_dates_datetime_objects(self):
        return [datetime.datetime.strptime(date, '%Y-%m-%d') for date in self.daily_dates]


#takes a water year's worth of a desired variable from NAM analysis data and 
#converts it into text files containing time series of the average value 
#of that variable within a deired lat-lon box. The resulting time series has 
#values every 6 hours starting at 00Z each day. The default setting is to make 
#a time series for every region in the region_data.list_regions() list. A new
#list can be used to create time series for fewer regions.
def nam_data_txt_files(year, var_name, var_units, var_id_num, var_dir, mask_water, region_list = region_data.list_regions()):
    var_name = var_name.lower()
    current_time = datetime.datetime(year - 1, 10, 1)
    end_time = datetime.datetime(year, 10, 1)
    times = []
    while current_time != end_time:
        times.append(str(current_time))
        current_time += datetime.timedelta(hours = 6)

    if mask_water == True:
        land_sea_mask = extract_nam_data.nam_grid(2022, '01', '01', '00', 437).grid
    else:
        land_sea_mask = None

    region_time_series = {}
    for region_name in region_list:
        region_time_series[region_name] = {'dates':[], 'hours':[], 'values':[]}
    
    n = 1
    for time in times:
        date = time.split(' ')[0]
        file_year, month, day = date.split('-')
        hour = time.split(' ')[1].split(':')[0]
        grid_data = extract_nam_data.nam_grid(file_year, month, day, hour, var_id_num)
        for region_name in region_time_series:
            region = region_data.region_data(region_name)
            region_time_series[region.name]['dates'].append(date)
            region_time_series[region_name]['hours'].append(hour)
            region_time_series[region_name]['values'].append(str(grid_data.latlon_domain_average(region.max_lat, region.min_lat, region.max_lon, region.min_lon, land_sea_mask)))
        if n % 4 == 0:
            print(var_name, date)
        n += 1

    print('Generating text files...')
    for region_name in region_time_series:
        region = region_data.region_data(region_name)
        file = save_files.open_write_file('/uufs/chpc.utah.edu/common/home/zpu-group25/mpye/nam_analysis_data/variable_time_series/' + var_dir + '/txt_files/' + str(year) + '_' + region.name + '_' + var_name.replace(' ', '_') + '.txt')
        file.write('#File created at: ' + str(datetime.datetime.utcnow()) + ' UTC\n')
        file.write('#File contains 6-hourly values of ' + var_name + ' during the ' + str(year) + ' water year within the ' + region.name.replace('_', ' ').title() + ' region.\n')
        file.write('#The Koppen climate zone found in the majority of this region is the ' + region.main_climate_zone + ' climate zone.\n')
        file.write('#This region is defined by the following latitudes and longitudes:\n')
        file.write('#       Max Latitude: ' + str(region.max_lat) + '\n')
        file.write('#       Min Latitude: ' + str(region.min_lat) + '\n')
        file.write('#       Max Longitude: ' + str(region.max_lon) + '\n')
        file.write('#       Max Longitude: ' + str(region.min_lon) + '\n')
        file.write('#The water year is defined from October 1 of the previous year to September 30 of the current year.\n')
        file.write('#Therefore, this file contains data from October 1, ' + str(year - 1) + ' through September 30, ' + str(year) + '.\n')
        file.write('#Format: date [YYYY-MM-DD], time [HH UTC], ' + var_name + ' [' + var_units + ']\n')
        file.write('#-----------------------------------------------------------------\n')
        for current_date, current_hour, current_value in zip(region_time_series[region.name]['dates'], region_time_series[region.name]['hours'], region_time_series[region.name]['values']):
            file.write(current_date + ', ' + current_hour +', ' + current_value + '\n')
        file.close()