import os


#Use this check to force the user to enter one of several provided options
def multiple_choice(message, correct_values):
    flag = False
    while flag == False:
        output = input(message)
        if output in correct_values:
            flag = True
        else:
            print('The value you entered is not an acceptable response. Please try again.')
    return output


#Frequently used form of the multiple_choice function where the options are yes or no
def y_n(message):
    return multiple_choice(message, ['y', 'n'])


#Use this check to force the user to enter an existing path
def path(message):
    path_exists = False
    while path_exists == False:
        path = input(message)
        path_exists = os.path.exists(path)
        if path_exists == False:
            print('The path you entered does not exist. Please reenter the desired path.')
    return path


#Use this to check to see if an existing path entered by the user exists but contains files with file names that are missing a desired string
def path_files_contain(message, desired_string = None):
    flag = False
    while flag == False:
        if desired_string == None:
            desired_string = input('Enter a string that must be contained in all file names of the desired path: ')
        new_path = path(message)
        flag = True
        for item in os.listdir(new_path):
            if desired_string not in item:
                flag = False
        if flag == False:
            print('The path you entered exists, but contains files missing "' + desired_string + '" in the file name. Please try again.')
            desired_string = None
    return new_path



#check to see is an entered values is between two other numbers
def check_range(value, minimum, maximum):
    if minimum != None and maximum != None:
        if minimum <= value <= maximum:
            return True
        else:
            return False
    elif minimum == None and maximum != None:
        if value <= maximum:
            return True
        else:
            return False
    elif minimum != None and maximum == None:
        if value >= minimum:
            return True
        else:
            return False


#Use this check to force the user to enter a value that can be converted into an integer
#if you would like to keep the value within a certain range, enter values for both minimum and maximum
#if you would like to set a minimum value, enter a value for minimum and enter "None" for maximum
#if you would like to set a maximum value, enter "None" for minimum and enter a value for maximum
def integer(message, minimum = None, maximum = None):
    is_int = False
    is_in_range = False
    while is_int == False or is_in_range == False:
        try:
            value = int(input(message))
            is_int = True
            is_in_range = True
            if minimum != None or maximum != None:
                is_in_range = check_range(value, minimum, maximum)
                if is_in_range == False:
                    print('The value you entered is out of range. Please try again.')
        except TypeError:
            is_int = False
            print('The value you entered cannot be converted to an integer. Please try again.')
    return value


#Use this check to force the user to enter a value that can be converted into a floating point number
#if you would like to keep the value within a certain range, enter values for both minimum and maximum
#if you would like to set a minimum value, enter a value for minimum and enter "None" for maximum
#if you would like to set a maximum value, enter "None" for minimum and enter a value for maximum
def floating_point(message, minimum = None, maximum = None):
    is_float = False
    is_in_range = False
    while is_float == False or is_in_range == False:
        try:
            value = float(input(message))
            is_float = True
            is_in_range = True
            if minimum != None or maximum != None:
                is_in_range = check_range(value, minimum, maximum)
                if is_in_range == False:
                    print('The value you entered is out of range. Please try again.')
        except TypeError:
            is_float = False
            print('The value you entered cannot be converted to a floating point number. Please try again.')
    return value