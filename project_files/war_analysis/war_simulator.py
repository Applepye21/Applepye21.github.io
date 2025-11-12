import random
import statistics as stat
import datetime


program_start_time = datetime.datetime.now(datetime.UTC)


#Creates a player to play each game and stores the players cards.
class player(object):
    def __init__(self, hand):
        self.draw_pile = hand
        self.win_pile = []
        self.initial_mean_card_value = stat.mean(hand)
        num_aces = 0
        for card in hand:
            if card == 14:
                num_aces += 1 
        self.initial_num_aces = num_aces
    
    #Takes cards from the win pile and shuffles them up to become 
    #the draw pile.
    def shuffle_win_pile(self):
        random.shuffle(self.win_pile)
        for card in self.win_pile:
            self.draw_pile.append(card)
        self.win_pile = []
    
    #Calculates the number of cards held by a player at a given 
    #time. Combines win and draw piles.
    def total_cards(self):
        return len(self.draw_pile) + len(self.win_pile)
        

#Checks to see if a player has run out of cards in their draw pile.
#If they have, it runs the shuffle_win_pile method.
def draw_pile_check(player):
    if len(player.draw_pile) == 0:
        player.shuffle_win_pile()


#Gives the winning player the cards they won.
def collect_cards(winner, win_cards):
    for card in win_cards:
        winner.win_pile.append(card)


#When a war occurs, this function puts the top thre cards from a 
#player into the win_cards list, which acts like the pot for the 
#round. If a player does not have enough cards in their draw pile,
#it shuffles in cards from their win pile. If there are stil not 
#enough cards, fewer cards are burned.
def burn(player, win_cards):
    if len(player.draw_pile) >= 4:
        for card in player.draw_pile[:3]:
            win_cards.append(card)
        del player.draw_pile[:3]
    elif len(player.draw_pile) < 4:
        player.shuffle_win_pile()
        if player.total_cards() >= 4:
            for card in player.draw_pile[:3]:
                win_cards.append(card)
            del player.draw_pile[:3]
        elif player.total_cards() < 4:
            for card in player.draw_pile[:-1]:
                win_cards.append(card)
            del player.draw_pile[:-1]
    return win_cards
        
 
#Stores information about the winner and the game for each game played.
#Format per game: winner, mean card value, number of initial aces, number of wars
#the losers info can be found using the winners info:
#loser's initial mean card value = 16 - winner's initial mean card value
#losers initial number of aces = 4 - winner's initial number of aces 
game_data_file = open('war_simulation_game_data.csv', 'w', encoding='utf-8')
game_data_file.write('Winner,Winner Initial Mean Card Value,Winner Initial Number of Aces,Loser Initial Mean Card Value,Number of Wars\n')
        

#Creates a "deck" of cards in order starting from 2 and ending at 14.
#All numbered cards are represented by their actual card value, jacks
#are 11, queens are 12, kings are 13, and aces are 14.
start_deck = []
n = 2
while int(n) <= 14:
    start_deck.append(int(n))
    n += 0.25
    

#"number_of_games" sets the number of games to be played and the while 
#loop runs exactly that number of games.
number_of_games = 1000000
alert_list = [i for i in range(10000, 1000000, 10000)]
game_number = 0
while game_number < number_of_games:
    
    #Shuffles the initial deck of cards randomly and deals cards to each player.
    random.shuffle(start_deck)
    hand_1 = []
    hand_2 = []
    last_deal = 2
    for card in start_deck:
        if last_deal == 2:
            hand_1.append(card)
            last_deal = 1
        elif last_deal == 1:
            hand_2.append(card)
            last_deal = 2
    player_1 = player(hand_1)
    player_2 = player(hand_2)
    
    #counts the number of wars per game
    war_ct = 0
    
    #Plays a game from start to finish
    while player_1.total_cards() != 0 and player_1.total_cards() != 52:
        #Checks to make sure the program isnt deleting or addding new cards anywhere.
        total_game_cards = player_1.total_cards() + player_2.total_cards()
        if total_game_cards != 52:
            print('the current number of cards is either too high or too low.')
            print('current number of cards: ' + str(total_game_cards))
            raise ValueError
        else:
            #Shuffles win pile cards into draw pile if needed
            draw_pile_check(player_1)
            draw_pile_check(player_2)
            #Stores cards that will be won during the round.
            win_cards = []
            #Decides who wins and gives the winner the cards they won.
            trick_winner = False
            while trick_winner == False:
                #Draws a card and deletes it from hand, putting it into the win cards pile.
                player_1_card = player_1.draw_pile[0]
                player_2_card = player_2.draw_pile[0]
                del player_1.draw_pile[0]
                del player_2.draw_pile[0]
                win_cards.append(player_1_card)
                win_cards.append(player_2_card)
                
                #Checks for winner
                if player_1_card > player_2_card:    #player 1 wins the trick
                    trick_winner = True
                    collect_cards(player_1, win_cards)
                elif player_2_card > player_1_card:    #player 2 wins the trick
                    trick_winner = True
                    collect_cards(player_2, win_cards)
                elif player_1_card == player_2_card:    #there is a war
                    if total_game_cards == 0:
                        trick_winner = None    
                    else:
                        war_ct += 1
                        win_cards = burn(player_1, win_cards)
                        win_cards = burn(player_2, win_cards)
                        if player_1.total_cards() == 0:
                            trick_winner = True
                            collect_cards(player_2, win_cards)
                        if player_2.total_cards() == 0:
                            trick_winner = True
                            collect_cards(player_1, win_cards)
                            
            #Appends information about the game to the historical_game_data list
            #player 1 wins the game
            if player_1.total_cards() == 52 and player_2.total_cards() == 0:
                game_data_file.write('Player 1,'  + str(player_1.initial_mean_card_value) + ',' + str(player_1.initial_num_aces) + ',' + str(player_2.initial_mean_card_value) + ',' + str(war_ct) + '\n')
            #player 2 wind the game
            elif player_1.total_cards() == 0 and player_2.total_cards() == 52:
                game_data_file.write('Player 2,' + str(player_2.initial_mean_card_value) + ',' + str(player_2.initial_num_aces) + ',' + str(player_1.initial_mean_card_value) + ',' + str(war_ct) + '\n')
            #the game is a tie
            #elif player_1.total_cards() == player_2.total_cards() == 0:
            elif trick_winner == None:
                game_data_file.write('Tie,' + str(player_1.initial_mean_card_value) + ',' + str(player_1.initial_num_aces) + ',' + str(player_2.initial_mean_card_value) + ',' + str(war_ct) + '\n')
                
    if game_number + 1 in alert_list:
        print(str(game_number + 1) + ' games played')
    game_number += 1
    player_1_card_amount = len(player_1.draw_pile) + len(player_1.win_pile)


#Ends program and calulates runtime
game_data_file.close()
program_end_time = datetime.datetime.now(datetime.UTC)
program_run_time = program_end_time - program_start_time
print('Program run time: ' + str(program_run_time))