import numpy as np
import input_check
import time


print('M A S T E R M I N D')

#set the default game parameters
code_length = 4
num_of_colors = 6
num_of_guesses = 10
repeat_colors = True

new_game = True
while new_game == True:
    print()
    print('Current game settings:')
    print('\t- Code length: ' + str(code_length))
    print('\t- Number of possible digit values: ' + str(num_of_colors))
    print('\t- Reapeat digit values: Yes')
    print('\t- Maximum number of gueses: ' + str(num_of_guesses))
    print()

    #Get user preferences
    defaults = input_check.y_n('Would you like to use the current game settings? (y/n): ')
    print()
    if defaults == 'n':
        change_code_length = input_check.y_n('Would you like to change the code length? (y/n): ')
        if change_code_length == 'y':
            code_length = input_check.integer('Enter a new value for code length (maximum of 7 and minimum of 3): ', 3, 7)
        print()
        change_num_of_colors = input_check.y_n('Would you like to change the number of possible digit values? (y/n): ')
        if change_num_of_colors == 'y':
            num_of_colors = input_check.integer('Enter a new value for the number of digit values (maximum of 10 and minimum of one plus the code length): ', 1 + code_length, 10)
        print()
        change_num_of_guesses = input_check.y_n('Would you like to change the maximum number of guesses? (y/n): ')
        if change_num_of_guesses == 'y':
            num_of_guesses = input_check.integer('Enter a new value for the maximum number of guesses (minimum of 1): ', minimum = 1)
        print()
        change_repeat_colors = input_check.y_n('Would you like to prevent digit values from repeating themselves in the code? (y/n): ')
        if change_repeat_colors == 'y':
            repeat_colors = True
        print()

    #generate the game code randomly and allow for no repeat codes
    code = ''
    for i in range(code_length):
        good_number = False
        while good_number == False:
            random_digit = str(np.random.randint(0, num_of_colors))
            good_number = True
            if repeat_colors == False:
                if random_digit in code:
                    good_number = False
        code += str(random_digit)

    #run the game
    print('-----START GAME-----')
    guess_num = 1
    game_status = 'running'
    while game_status == 'running':
        #enter a guess and check to make sure it meets the requirements of 
        #the code before allowing the game to continue
        good_guess = False
        while good_guess == False:
            print()
            print('Guess: ' + str(guess_num))
            guess = input('Enter a ' + str(code_length) + '-digit number: ') 
            if len(guess) == len(code):
                try:
                    int(guess)
                    good_guess = True
                    good_colors = True
                    for value in guess:
                        if good_colors == True:
                            if int(value) >= num_of_colors:
                                good_guess = False
                                good_colors = False
                                print('At least one of the digits in your guess had a value higher than ' + str(num_of_colors - 1) + '. Try again and make sure all digits have a value of ' + str(num_of_colors - 1) + ' or less')
                except ValueError:
                    good_guess = False
                    print('You did not enter a number! Try again and enter a number!')
            else:
                good_guess = False
                print('You did not enter a number with ' + str(code_length) + ' digits! Try again!')
        
        #respond to the guess
        if guess_num == num_of_guesses:
            time.sleep(3)
        if guess == code:
            game_status = 'won'
            print('Correct!')
            print('You win!')
        else:
            if guess_num == num_of_guesses:
                game_status = 'lost'
                print('You lose! :(')
                print('The code was: ' + code)
            else:
                #check to see how close the guess was to the code
                right_color_right_place = 0
                right_color_wrong_place = 0
                n = 0
                code_checked_pegs = []
                guess_checked_pegs = []
                #check to see if any of the pegs are in the right position
                #with the right color
                while n < len(guess):
                    if code[n] == guess[n]:
                        right_color_right_place += 1
                        code_checked_pegs.append(n)
                        guess_checked_pegs.append(n)
                    n += 1
                #check to see if any of the pegs have the correct color but
                #are in the wrong location
                n = 0
                while n < len(guess):
                    m = 0
                    while m < len(code):
                        if m not in code_checked_pegs and n not in guess_checked_pegs:
                            if m != n:
                                if code[m] == guess[n]:
                                    right_color_wrong_place += 1
                                    code_checked_pegs.append(m)
                                    guess_checked_pegs.append(n)
                        m += 1
                    n += 1
                print('Correct digit value and position: ' + str(right_color_right_place))
                print('Correct digit value wrong position: ' + str(right_color_wrong_place))
                print('Remaining guesses: ' + str(num_of_guesses - guess_num))
            
        guess_num += 1

    print()
    print('-----End Game-----')
    print()

    new_game_check = input_check.y_n('Would you like to start a new game? (y/n):')
    if new_game_check == 'y':
        print()
    elif new_game_check == 'n':
        new_game = False
        print()
        print('Thanks for playing!')
        print()
    
        
