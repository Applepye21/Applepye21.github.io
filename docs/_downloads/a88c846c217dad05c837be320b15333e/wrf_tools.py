import os
import wrf
import netCDF4
import numpy as np
import netcdf_files
import datetime
import my_stats
import webbrowser as web


###CLASSES###

#creates an object to store WRF data grids of several desired variables
#var_list defines the variables desired while layer_list specifies the
#desired layer index within a 3-D grid for the corresponding variable.
#If the layer is a soil layer the layer should be specified as an integer
#between 0 and 3, 0 for top soil and 3 for the lowest soil layer.
#For atmospheric layers, the layer should be specified as a string with
#the value of the layer followed by an underscore and then the coordinate
#string. The possible coordinate strings are:
#	-pressure: 'p'
#	-km ASL: 'asl'
#	-km AGL: 'agl'
#	-potential temperature: 'theta'
#	-equivalent potential temperature: 'thetae'
#For example: 500 mb would be '500_p' and 100m agl would be '0.1_agl'.
#If geopotential height is the desired variable, enter 'Z' as the variable
#name in the var list. It is a derived quantity from other WRF variables.
#if the variable only has a 2_d array attached to it, enter "None" for
#the variable's layer in the layer_list. The same goes for 'PRCP' which
#is derrived from the WRF data and represents the total precipitation.
class wrf_var_grids(object):
	def __init__(self, var_list, layer_list):
		self.var_list = var_list
		self.var_grids = {}
		self.var_layers = {}
		for var, layer in zip(var_list, layer_list):
			self.var_layers[var] = layer
		self.dates = []
		self.times = []

	#provides WRF data to be stored based upon the file path passed
	def add_data(self, wrf_file_path):
		wrf_data = netCDF4.Dataset(wrf_file_path)

		date, time = wrf_file_path.split('/')[-1].split('_')[-2:]
		self.dates.append(date)
		self.times.append(time)

		for var in self.var_list:
			if var != 'PRCP':
				if self.var_layers[var] == None:
					var_data = wrf.getvar(wrf_data, var, meta = False)[:, :]
				else:
					if type(self.var_layers[var]) == type(0):
						var_data = wrf.getvar(wrf_data, var, meta = False)[self.var_layers[var], :, :]
					elif type(self.var_layers[var]) == type('str'):
						layer_value, layer_type = self.var_layers[var].split('_')
						if layer_type == 'asl':
							layer_type = 'ght_msl'
						elif layer_type == 'agl':
							layer_type = 'ght_agl'
						if '.' in layer_value:
							layer_value = float(layer_value)
						else:
							layer_value = int(layer_value)

						if var == 'Z':
							var_data_3d = wrf.getvar(wrf_data, 'z', meta = False)
						else:
							var_data_3d = wrf.getvar(wrf_data, var, meta = False)
						if layer_type == 'p':
							pressure_data = wrf.getvar(wrf_data, 'pressure', meta = False)
							var_data = wrf.interplevel(var_data_3d, pressure_data, layer_value, meta = False)
						else:
							var_data = wrf.vinterp(wrf_data, var_data_3d, layer_type, [layer_value])

			elif var == 'PRCP':
				var_data = wrf.getvar(wrf_data, 'RAINC', meta = False)[:, :] + wrf.getvar(wrf_data, 'RAINNC', meta = False)[:, :]

			if var not in self.var_grids:
				self.var_grids[var] = var_data
			else:
				var_data = var_data[np.newaxis, :, :]
				try:
					self.var_grids[var] = np.vstack((self.var_grids[var], var_data))
				except ValueError:
					self.var_grids[var] = np.vstack((self.var_grids[var][np.newaxis, :, :], var_data))

		if hasattr(self, 'lats') == False:
			self.lats, self.lons = wrf.latlon_coords(wrf.getvar(wrf_data, 'T2'))
		if hasattr(self, 'land_mask') == False:
			self.land_mask = wrf.getvar(wrf_data, 'LANDMASK')

		wrf_data.close()

	#creates a list of unique dates that represent the data
	def daily_dates(self):
		unique_dates = []
		for date in self.dates:
			if date not in unique_dates:
				unique_dates.append(date)
		return unique_dates

	#creates a list of datetime objects representative of every time represented
	#in the data set
	def datetime_objects(self):
		datetime_object_list = []
		for date, time in zip(self.dates, self.times):
			datetime_str = date + ' ' + time
			datetime_object_list.append(datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S'))
		return datetime_object_list

	#creates a list of datetime objects that represent each unique date in the
	#data set
	def daily_datetime_objects(self):
		datetime_object_list = []
		for date in self.daily_dates():
			datetime_object_list.append(datetime.datetime.strptime(date, '%Y-%m-%d'))
		return datetime_object_list

	#creates a new variable that reports the qpf at a desired time interval.
	#All QPF layers where the start of the QPF period is not included in the
	#wrf_var_grids object will be marked as NaN.
	#The type of precipitation can be changed by selecting "RAINC" (Convective precip)
	#or "RAINNC" (non-convective precip) instead of "PRCP" (total precip)
	def qpf_calc(self, interval_hours, precip_type = 'PRCP'):
		assert precip_type in self.var_grids, precip_type + ' must be included as a key in the var_grids attribute to run qpf_calc with the precip type set to ' + precip_type  + '.'
		self.var_grids[str(interval_hours) + '_hr_qpf'] = np.zeros(self.var_grids[precip_type].shape)
		interval = datetime.timedelta(hours = interval_hours)
		dates = self.datetime_objects()
		for i in range(len(dates)):
			current_date = dates[i]
			interval_start_date = current_date - interval
			interval_start_index = None
			for j in range(len(dates)):
				if dates[j] == interval_start_date:
					interval_start_index = j
			if interval_start_index != None:
				qpf_data = self.var_grids[precip_type][i, :, :] - self.var_grids[precip_type][interval_start_index, :, :]
			elif interval_start_index == None:
				qpf_data = np.ones(self.var_grids[precip_type][0, :, :].shape) * np.nan
			self.var_grids[str(interval_hours) + '_hr_qpf'][i, :, :] = qpf_data
		return self

	#creates arrays that represent each day in a data set as opposed to
	#each time step by either averageing the data for each data or finding
	#finding the maximum or minimum value for each day at each grid point.
	#If a daily data set is not desired for all variables, a list of variables
	#where daily data sets are desired can be passed to the var_list parameter.
	def daily_data(self, method = 'mean', var_list = None):
		if var_list == None:
			var_list = self.var_list
		dates = self.daily_dates()
		daily_var_grids = {}
		for var in var_list:
			n = 0
			last_date = dates[0]
			for current_date in self.dates:
				current_array = self.var_grids[var][n, :, :][np.newaxis, :, :]
				if current_date == last_date:
					try:
						today_grids = np.vstack((today_grids, current_array))
					except UnboundLocalError:
						today_grids = current_array
				elif current_date != last_date:
					if method == 'mean':
						day_values = np.mean(today_grids, axis = 0)[np.newaxis, :, :]
					elif method == 'max':
						day_values = np.max(today_grids, axis = 0)[np.newaxis, :, :]
					elif method == 'min':
						day_values = np.min(today_grids, axis = 0)[np.newaxis, :, :]
					try:
						daily_grids = np.vstack((daily_grids, day_values))
					except UnboundLocalError:
						daily_grids = day_values
					today_grids = current_array
				last_date = current_date
				n += 1
			try:
				if method == 'mean':
					daily_var_grids[var] = np.vstack((daily_grids, np.mean(today_grids, axis = 0)[np.newaxis, :, :]))
				elif method == 'max':
					daily_var_grids[var] = np.vstack((daily_grids, np.max(today_grids, axis = 0)[np.newaxis, :, :]))
				elif method == 'min':
					daily_var_grids[var] = np.vstack((daily_grids, np.min(today_grids, axis = 0)[np.newaxis, :, :]))
			except UnboundLocalError:
				if method == 'mean':
					daily_var_grids[var] = np.mean(today_grids, axis = 0)[np.newaxis, :, :]
				elif method == 'max':
					daily_var_grids[var] = np.max(today_grids, axis = 0)[np.newaxis, :, :]
				elif method == 'min':
					daily_var_grids[var] = np.min(today_grids, axis = 0)[np.newaxis, :, :]
		return daily_var_grids

	#creates arrays that represent each month in a data set as opposed to
	#each time step by either averageing the data for each data or finding
	#finding the maximum or minimum value for each month at each grid point.
	#If a monthly data set is not desired for all variables, a list of variables
	#where monthly data sets are desired can be passed to the var_list parameter.
	def monthly_data(self, method = 'mean', var_list = None):
		if var_list == None:
			var_list = self.var_list
		dates = self.daily_dates()
		monthly_var_grids = {}
		for var in var_list:
			n = 0
			last_month = dates[0].split('-')[1]
			for current_date in self.dates:
				current_month = current_date.split('-')[1]
				current_array = self.var_grids[var][n, :, :][np.newaxis, :, :]
				if current_month == last_month:
					try:
						month_grids = np.vstack((month_grids, current_array))
					except UnboundLocalError:
						month_grids = current_array
				elif current_month != last_month:
					if method == 'mean':
						month_values = np.mean(month_grids, axis = 0)[np.newaxis, :, :]
					elif method == 'max':
						month_values = np.max(month_grids, axis = 0)[np.newaxis, :, :]
					elif method == 'min':
						month_values = np.min(month_grids, axis = 0)[np.newaxis, :, :]
					try:
						monthly_grids = np.vstack((monthly_grids, month_values))
					except UnboundLocalError:
						monthly_grids = month_values
					month_grids = current_array
				last_month = current_month
				n += 1
			try:
				if method == 'mean':
					monthly_var_grids[var] = np.vstack((monthly_grids, np.mean(month_grids, axis = 0)[np.newaxis, :, :]))
				elif method == 'max':
					monthly_var_grids[var] = np.vstack((monthly_grids, np.max(month_grids, axis = 0)[np.newaxis, :, :]))
				elif method == 'min':
					monthly_var_grids[var] = np.vstack((monthly_grids, np.min(month_grids, axis = 0)[np.newaxis, :, :]))
			except UnboundLocalError:
				if method == 'mean':
					monthly_var_grids[var] = np.mean(month_grids, axis = 0)[np.newaxis, :, :]
				elif method == 'max':
					monthly_var_grids[var] = np.max(month_grids, axis = 0)[np.newaxis, :, :]
				elif method == 'min':
					monthly_var_grids[var] = np.min(month_grids, axis = 0)[np.newaxis, :, :]
		return monthly_var_grids


	#creates a list of rows and columns to define the grid coords within a desired
	#bbox. The lat-lon bbox should be passed to the method like so:
	#[min_lat, max_lat, min_lon, max_lon]
	def regional_rows_and_cols(self, bbox):
		min_lat, max_lat, min_lon, max_lon = bbox
		rows = []
		cols = []
		print('Searching for grid coords within the following lat-lon bbox: ' + str(bbox))
		for row in range(self.lats.shape[0]):
			for col in range(self.lats.shape[1]):
				if min_lat <= self.lats[row, col] <= max_lat:
					if min_lon <= self.lons[row, col] <= max_lon:
						rows.append(row)
						cols.append(col)
		print('All grid coords found successfully!')
		return rows, cols

	#creates a time series of the average conditions of a collection of grid points.
	#The grid points that are selected are defined by the rows and cols parameters.
	#The grid points within a lat-lon bbox can (and should) be obtained using the
	#regional_rows_and_cols() method.
	#if a regional time series is not desired for every variable, provide a list of
	#the desired variables to the var_list parameter.
	def regional_average_time_series(self, rows, cols, var_list = None):
		time_series_dict = {}
		if var_list == None:
			var_list = self.var_list
		for var in var_list:
			for time_step in range(len(self.times)):
				regional_values = []
				for row, col in zip(rows, cols):
					regional_values.append(self.var_grids[var][time_step, row, col])
				if var in time_series_dict.keys():
					time_series_dict[var].append(my_stats.mean(regional_values))
				elif var not in time_series_dict.keys():
					time_series_dict[var] = [my_stats.mean(regional_values)]
		return time_series_dict

	#converts values over water to np.nan. The variables affected should be
	#listed in the var_list parameter. Note that this method permanently
	#alters the data stored within the var_grids attribute.
	def mask_water(self, var_list = None):
		if var_list == None:
			var_list = self.var_list
		nan_mask = np.where(self.land_mask == 0, np.nan, self.land_mask)
		for var in var_list:
			self.var_grids[var] = self.var_grids[var] * nan_mask

	#converts values over land to np.nan. The variables affected should be
	#listed in the var_list parameter. Note that this method permanently
	#alters the data stored within the var_grids attribute.
	def mask_land(self, var_list = None):
		if var_list == None:
			var_list = self.var_list
		nan_mask = np.where(self.land_mask == 1, np.nan, self.land_mask)
		for var in var_list:
			self.var_grids[var] = self.var_grids[var] * nan_mask


#Creates a series of wrf_var_grids objects for each hour so that all data within
#each object only represents one hour of the day.
class diurnal_grids(object):
	def __init__(self, var_list, layer_list, hour_list):
		self.var_list = var_list
		self.hour_grids = {}
		for hour in hour_list:
			self.hour_grids[hour] = wrf_var_grids(var_list, layer_list)

	def add_data(self, wrf_file_path):
		file_hour = wrf_file_path.split('_')[-1].split(':')[0]
		self.hour_grids[file_hour].add_data(wrf_file_path)


#Creates an object that stores entire 3D arrays for a single time step
class wrf_var_grids_3d(object):
	def __init__(self, var_list, wrf_file_path):
		self.var_list = var_list
		self.var_grids = {}

		wrf_data = netCDF4.Dataset(wrf_file_path)
		self.date, self.time = wrf_file_path.split('/')[-1].split('_')[-2:]

		for var in self.var_list:
			self.var_grids[var] = wrf.getvar(wrf_data, var, meta = False)[:, :, :]

		if hasattr(self, 'lats') == False:
			self.lats, self.lons = wrf.latlon_coords(wrf.getvar(wrf_data, 'ua'))

		wrf_data.close()


###FUNCTIONS###

#creates a list of file names within a certain range of dates. To make a
#list of file paths, pass the file directory path to "wrf_dir_file_path".
#To specify certain times of day, pass a new "times_list" that contains
#only the specific times of day desired. If the data comes from a domain
#other than d01, pass the domain name to the "domain" parameter.
def select_wrf_files(start_date, end_date, times_list = ['00', '03', '06', '09', '12', '15', '18', '21'], domain = 'd01', wrf_file_dir_path = ''):
	current_date_object = datetime.datetime.strptime(start_date, '%Y-%m-%d')
	end_date_object = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days = 1)
	desired_dates = []
	while current_date_object != end_date_object:
		desired_dates.append(datetime.datetime.strftime(current_date_object, '%Y-%m-%d'))
		current_date_object += datetime.timedelta(days = 1)

	file_names = []
	for date in desired_dates:
		for time in times_list:
			wrf_file_path = wrf_file_dir_path + 'wrfout_' + domain + '_' + date + '_' + time + ':00:00'
			if os.path.exists(wrf_file_path) == True:
				file_names.append(wrf_file_path)
	return file_names


#creates a wrf_var_grids object with data between a given start date and end date
#Descriptions for each parameter can be found in the secriptions for the
#select_wrf_files function and the wrf_var_grids class
def time_select_var_grids(wrf_file_dir_path, start_date, end_date, var_list, layer_list, times_list = ['00', '03', '06', '09', '12', '15', '18', '21']):
	wrf_file_paths = select_wrf_files(start_date, end_date, times_list = times_list, wrf_file_dir_path = wrf_file_dir_path)
	data = wrf_var_grids(var_list, layer_list)
	for file_path in wrf_file_paths:
		data.add_data(file_path)
		print('Data from ' + file_path.split('/')[-1] + ' extracted!')
	return data


#creates a list of start days and a list of end days at regular intervals between
#two dates. The interval should be given in units of days
def start_end_date_lists(start_date, end_date, interval):
	start_date_list = [start_date]
	end_date_list = []
	current_date_object = datetime.datetime.strptime(start_date, '%Y-%m-%d')
	end_date_object = datetime.datetime.strptime(end_date, '%Y-%m-%d')
	day_num = 0
	while current_date_object != end_date_object:
		day_num += 1
		if day_num % interval == 0:
			start_date_list.append(datetime.datetime.strftime(current_date_object + datetime.timedelta(days = 1), '%Y-%m-%d'))
			end_date_list.append(datetime.datetime.strftime(current_date_object, '%Y-%m-%d'))
			day_num = 0
		current_date_object += datetime.timedelta(days = 1)
	if end_date not in end_date_list:
		end_date_list.append(end_date)
	return start_date_list, end_date_list


#lists all the variables in the wrf file
def list_vars(wrf_file_path):
	ncfile = netCDF4.Dataset(wrf_file_path)
	print('Note: total precipitation is not included in any of these lists. For total precip, enter "PRCP" as the variable code at the next prompt')
	for var in ncfile.variables.keys():
		print(var)
	ncfile.close()


#Takes 3D arrays of either zonal or meridional wind and mixing ratio and
#returns a 2D array of zonal or meridional integrated vapor transport.
#NOTE: wind must be in units of m/s, mixing ratio must be in units of
#kg/kg, and pressure must be in units of Pa
def calc_ivt(wind_array, mixing_ratio_array, pressure_array):
	specific_humidity_array = mixing_ratio_array / (1 + mixing_ratio_array)
	ivt = np.zeros((wind_array.shape[1], wind_array.shape[2]))
	g = 9.81	#gravitational acceleration in m/s^2
	n = 1
	while n < wind_array.shape[0]:
		top_v = wind_array[n, :, :]
		bot_v = wind_array[n - 1, :, :]
		top_q = specific_humidity_array[n, :, :]
		bot_q = specific_humidity_array[n - 1, :, :]
		top_p = pressure_array[n, :, :]
		bot_p = pressure_array[n - 1, :, :]

		v = (top_v + bot_v) / 2
		q = (top_q + bot_q) / 2
		delta_p = bot_p - top_p
		ivt += v * q * delta_p

		n += 1
	return ivt / g


#Takes 3D arrays of mixing ratio and atmospheric pressure and returns a 2D
#array of precipitable water in units of meters.
#NOTE:mixing ratio must be in units of kg/kg, and pressure must be in
#units of Pa
def calc_pwat(mixing_ratio_array, pressure_array):
	specific_humidity_array = mixing_ratio_array / (1 + mixing_ratio_array)
	pwat = np.zeros((pressure_array.shape[1], pressure_array.shape[2]))
	g = 9.81	#gravitational acceleration in m/s^2
	rho = 997	#density of water in kg/m^3
	n = 1
	while n < pressure_array.shape[0]:
		top_q = specific_humidity_array[n, :, :]
		bot_q = specific_humidity_array[n - 1, :, :]
		top_p = pressure_array[n, :, :]
		bot_p = pressure_array[n - 1, :, :]

		q = (top_q + bot_q) / 2
		delta_p = bot_p - top_p
		pwat += q * delta_p

		n += 1
	return pwat / (rho * g)
