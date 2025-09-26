import os
import numpy as np
import datetime
import pygrib
import sys
sys.path.insert(1, '/uufs/chpc.utah.edu/common/home/zpu-group25/mpye/base_scripts')
import my_stats


#Creates a numpy array of entire NAM domain for desired time and variable along
#with associated latitude and longitude grids. The value for var_id_num can be
#found by using the search_vars function and entering the value assicated with
#the desired variable
class nam_grid(object):
    def __init__(self, year, month, day, hour, var_id_num):
        date = str(year) + month + day
        if int(month) > 9:
            year = int(year) + 1
        grib_data = pygrib.open('/uufs/chpc.utah.edu/common/home/zpu-group25/mpye/nam_analysis_data/raw_data/' + str(year) + '_data/' + date + '.nam.t' + hour + 'z.awphys00.tm00.grib2')
        var_data = grib_data.select()[int(var_id_num) - 1]
        self.grid = np.array(var_data.values)
        self.lats, self.lons = var_data.latlons()
        self.land_sea_mask = np.array(grib_data.select()[436].values)
        grib_data.close()

    #Takes the average of all values in the variable grid within a desired Latitude
    #Longitude box and returns the average value. Ignores values over water if desired
    #using the land_sea_mask parameter. Enter a land sea mask grid as the parameter if
    #you would like to exclude values over water. Otherwise, enter None
    def latlon_domain_average(self, max_lat, min_lat, max_lon, min_lon, land_sea_mask):
        values = []
        flat_grid = self.grid.flatten()
        flat_lats = self.lats.flatten()
        flat_lons = self.lons.flatten()
        if str(type(land_sea_mask)) != "<class 'NoneType'>":
            land_sea_mask = land_sea_mask.flatten()
            for value, lat, lon, mask in zip(flat_grid, flat_lats, flat_lons, land_sea_mask):
                if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon and mask == 1:
                    values.append(value)
        else:
            for value, lat, lon in zip(flat_grid, flat_lats, flat_lons):
                if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                    values.append(value)
        return my_stats.mean(values)

    #Sets the value of grid points over water to np.nan
    def mask_water(self):
        self.grid = self.grid * np.where(self.land_sea_mask == 0, np.nan, self.land_sea_mask)

    #Sets the value of grid points over land to np.nan
    def mask_land(self):
        self.grid = self.grid * np.where(self.land_sea_mask == 1, np.nan, self.land_sea_mask)


#times list is set to a default of all times but can be changed to show different times
def average_condition_grid(start_date, end_date, var_id_num, times_list = ['00', '06', '12', '18']):
    current_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days = 1)
    date_list = []
    while current_date != end_date:
        for time in times_list:
            date_list.append(current_date + datetime.timedelta(hours = int(time)))
        current_date = current_date + datetime.timedelta(days = 1)

    for date in date_list:
        year, month, day, hour = datetime.datetime.strftime(date, '%Y-%m-%d-%H').split('-')
        try:
            sum_grid += nam_grid(year, month, day, hour, var_id_num).grid
        except NameError:
            sum_grid = nam_grid(year, month, day, hour, var_id_num).grid
        print(var_id_num, date)
    return sum_grid / len(date_list)




#Prints variables and their assciate ID number to the terminal to view possible
#variables. A string can be passed to the function that will restrict the output
#to only variables that contain that particular string. Make sure all characters
#in the search string are entered as lowercase.
def search_vars(search_str = None):
    grib_data = pygrib.open('/uufs/chpc.utah.edu/common/home/zpu-group25/mpye/nam_analysis_data/raw_data/2022_data/20220101.nam.t00z.awphys00.tm00.grib2')
    print()
    if search_str == None:
        for item in grib_data.select():
            print(item)
            print()
    else:
        for item in grib_data.select():
            item_str = str(item).lower()
            if search_str in item_str:
                print(item)
                print()
