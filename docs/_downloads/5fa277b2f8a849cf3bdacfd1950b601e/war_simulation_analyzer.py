import statistics as stat
import matplotlib.pyplot as plot
import numpy as np
import pandas as pd
    

#separates data into bins based on quantiles and returns a dictionary of the binned data
def bin_separator(data, quantiles):
    bins = {}
    for mean in data:
        #catches means that fall in the first quantile
        if mean < quantiles[0]:
            try:
                bins['4.50-' + str(quantiles[0])].append(mean)
            except KeyError:
                bins['4.50-' + str(quantiles[0])] = [mean]
        #catches means that fall in the last quantile
        elif mean >= quantiles[-1]:
            try:
                bins[str(quantiles[-1]) + '-11.50'].append(mean)
            except KeyError:
                bins[str(quantiles[-1]) + '-11.50'] = [mean]
        #catches means that fall in the middle quantiles
        else:
            flag = False
            n = 0
            while flag == False:
                if quantiles[n] <= mean < quantiles[n + 1]:    #looks for the correct bin for the mean and adds the data to the bin when the correct bin is found
                    flag = True
                    try:
                        bins[str(quantiles[n]) + '-' + str(quantiles[n + 1])].append(mean)
                    except KeyError:
                        bins[str(quantiles[n]) + '-' + str(quantiles[n + 1])] = [mean]
                else:
                    n += 1
    return bins


#calculates the slope of a linear regression line given x and y data
def regression_slope(x, y):     
    x_mean = stat.mean(x)
    y_mean = stat.mean(y)
    slope_numerator = 0
    slope_denominator = 0
    n = 0
    while n < len(x):
        slope_numerator += ((x[n] - x_mean) * (y[n] - y_mean))
        slope_denominator += ((x[n] - x_mean)**2)
        n += 1
    slope = slope_numerator / slope_denominator
    return slope


#extract game data from csv file
historical_game_data = pd.read_csv('war_simulation_game_data.csv')
number_of_games = len(historical_game_data['Winner'].values)

#calculate number of wins for each player and ties
winners = historical_game_data['Winner'].value_counts()
player_1_win_ct = winners.get('Player 1', 0)
player_2_win_ct = winners.get('Player 2', 0)
total_wins = player_1_win_ct + player_2_win_ct
tie_ct = winners.get('Tie', 0)

#calculate win and lose means and medians
win_means = historical_game_data['Winner Initial Mean Card Value'].to_numpy()
lose_means = historical_game_data['Loser Initial Mean Card Value'].to_numpy()
all_means = np.concatenate((win_means, lose_means))
all_mean = np.mean(all_means)
win_mean = np.mean(win_means)
lose_mean = np.mean(lose_means)
all_median = np.median(all_means)
win_median = np.median(win_means)
lose_median = np.median(lose_means)
#count the number of winning initial card means larger than 8
mean_larger_8_ct = len(['0' for mean in win_means if mean > 8])

winner_start_aces = historical_game_data['Winner Initial Number of Aces'].value_counts()
#calculate number of wins by starting ace count
ace0_wins = winner_start_aces.get(0, 0)
ace1_wins = winner_start_aces.get(1, 0)
ace2_wins = winner_start_aces.get(2, 0)
ace3_wins = winner_start_aces.get(3, 0)
ace4_wins = winner_start_aces.get(4, 0)
#calculate total number of games played with each starting ace count
ace0_total = ace0_wins + ace4_wins
ace1_total = ace1_wins + ace3_wins
ace2_total = ace2_wins * 2
ace3_total = ace3_wins + ace1_wins
ace4_total = ace4_wins + ace0_wins

#makes a numpy array of war counts per game
wars_per_game = historical_game_data['Number of Wars'].to_numpy()


print('Data extracted and win counts by category calculated! Calculating game victory statistics...')


#sorts winning mean values and losing mean values into labeled bins and calculates chance of winning
means_quantiles = [q for q in np.quantile(list(win_means) + list(lose_means), q = np.arange(0.05, 1, 0.05))]
win_bins = bin_separator(win_means, means_quantiles)
lose_bins = bin_separator(lose_means, means_quantiles)
bin_percentages = {}
ordered_bin_keys = sorted(list(win_bins))
for bin_key in ordered_bin_keys:
    bin_percentages[bin_key] = 100 * (len(win_bins[bin_key]) / (len(win_bins[bin_key]) + len(lose_bins[bin_key])))

#calculates chance of winning with an initial average card value larger than 8
mean_larger_8_win_chance = (mean_larger_8_ct / number_of_games) * 100

#calculates the chance of winning based on the number of aces dealt
ace0_win_chance = (ace0_wins / ace0_total) * 100
ace1_win_chance = (ace1_wins / ace1_total) * 100
ace2_win_chance = (ace2_wins / ace2_total) * 100
ace3_win_chance = (ace3_wins / ace3_total) * 100
ace4_win_chance = (ace4_wins / ace4_total) * 100
ace_win_chance = [ace0_win_chance, ace1_win_chance, ace2_win_chance, ace3_win_chance, ace4_win_chance]


print('Game victory statistics calculated! Calculating win chance changes per war...')


#creates a list of all unique war counts and another indication the number of games at each war count 
war_ct_complete_values = []    #stores all unique war counts
war_ct_complete_counts = []    #stores the number of games at each war count
for ct in range(min(wars_per_game), max(wars_per_game) + 1):
    games_at_current_ct = list(wars_per_game).count(ct)
    if games_at_current_ct > 0:    #only adds war counts that have games with the coorresponding war count
        war_ct_complete_values.append(ct)
        war_ct_complete_counts.append(games_at_current_ct)

#sets the range of war counts to calculate the linear regression slopes over
max_war_ct_for_regression = 43        #43 represents the 95 percentile war count. Values above this are ignored to prevent outliers from skewing the results
min_war_ct_for_regression = 0

#computes the change in percent chance of winning for every initial average card value bin as a function of war count
bin_slopes = []
for bin_name in ordered_bin_keys:
    bin_min = float(bin_name.split('-')[0])
    bin_max = float(bin_name.split('-')[1])
    if bin_max == 11.5:
        bin_max = 12
    if bin_min == 4.5:
        bin_min = 4
    percentages_at_war_ct = []    #stores the percent chance of winning at each war count for a given initial average card value bin
    non_zero_war_cts = []    #stores war counts that have games played for a given initial average card value bin
    for war_ct in war_ct_complete_values[min_war_ct_for_regression:max_war_ct_for_regression + 1]:
        wins_at_war_ct = historical_game_data.loc[(historical_game_data['Winner Initial Mean Card Value'] >= bin_min) & (historical_game_data['Winner Initial Mean Card Value'] < bin_max) & (historical_game_data['Number of Wars'] == war_ct)]    #creates a dataframe of the wins with a given initial average card value bin and war_ct
        losses_at_war_ct = historical_game_data.loc[(historical_game_data['Loser Initial Mean Card Value'] >= bin_min) & (historical_game_data['Loser Initial Mean Card Value'] < bin_max) & (historical_game_data['Number of Wars'] == war_ct)]    #creates a dataframe of the losses with a given initial average card value bin and war_ct    
        if len(wins_at_war_ct['Number of Wars']) > 0 and len(losses_at_war_ct['Number of Wars']) > 0:    
            percentages_at_war_ct.append(100 * (len(wins_at_war_ct) / (len(wins_at_war_ct) + len(losses_at_war_ct))))
            non_zero_war_cts.append(war_ct)
    bin_slopes.append(regression_slope(non_zero_war_cts, percentages_at_war_ct))
    
    
#computes the change in percent chance of winning for every number of aces dealt as a function of war count
ace_slopes = []
for ace_ct in range(5):
    ace_percentages_at_war_ct = []    #stores the percent chance of winning at each war count for a given number of aces dealt
    non_zero_war_cts = []    #stores war counts that have games played for a given number of aces dealt
    for war_ct in war_ct_complete_values[min_war_ct_for_regression:max_war_ct_for_regression + 1]:
        ace_wins_at_war_ct = historical_game_data.loc[(historical_game_data['Winner Initial Number of Aces'] == ace_ct) & (historical_game_data['Number of Wars'] == war_ct)]    #creates a dataframe of the wins with a given ace_ct and war_ct
        ace_losses_at_war_ct = historical_game_data.loc[(historical_game_data['Winner Initial Number of Aces'] == 4 - ace_ct) & (historical_game_data['Number of Wars'] == war_ct)]    #creates a dataframe of the losses with a given ace_ct and war_ct
        if len(ace_wins_at_war_ct['Number of Wars']) > 0 and len(ace_losses_at_war_ct['Number of Wars']) > 0:
            ace_percentages_at_war_ct.append(100 * (len(ace_wins_at_war_ct) / (len(ace_wins_at_war_ct) + len(ace_losses_at_war_ct))))
            non_zero_war_cts.append(war_ct)
    ace_slopes.append(regression_slope(non_zero_war_cts, ace_percentages_at_war_ct))

#round bin edge values to 3 decimal places for plotting
rounded_bin_edges = []
for bin_key in bin_percentages.keys():
    bin_min = round(float(bin_key.split('-')[0]), 3)
    bin_max = round(float(bin_key.split('-')[1]), 3)
    rounded_bin_edges.append(str(bin_min) + '-' + str(bin_max))


print('Win chance changes per war calculated! Generating statistics report and plots...')


#writes statistics report to a text file
stat_file = open('all_game_stats.txt', 'w')
stat_file.write('War Simulation Statistics Report:\n\n')
stat_file.write('Total games played: ' + str(number_of_games) + '\n')
stat_file.write('Games won by Player 1: ' + str(player_1_win_ct) + '\n')
stat_file.write('Games won by Player 2: ' + str(player_2_win_ct) + '\n')
stat_file.write('tie games: ' + str(tie_ct) + '\n\n')
stat_file.write('Overall mean initial card value: ' + str(all_mean) + '\n')
stat_file.write('Overall median initial card value: ' + str(all_median) + '\n\n')
stat_file.write('Mean winning value: ' + str(win_mean) + '\n')
stat_file.write('Median winning value: ' + str(win_median) + '\n')
stat_file.write('Max Win Mean: ' + str(max(win_means)) + '\n')
stat_file.write('Min Win Mean: ' + str(min(win_means)) + '\n')
stat_file.write('Chance of winning with a mean larger than 8: %.2f' % mean_larger_8_win_chance + '%\n\n')
stat_file.write('Mean losing value: ' + str(lose_mean) + '\n')
stat_file.write('Median losing value: ' + str(lose_median) + '\n')
stat_file.write('Max Lose Mean: ' + str(max(lose_means)) + '\n')
stat_file.write('Min Lose Mean: ' + str(min(lose_means)) + '\n\n')
stat_file.write('Chance of winning with 0 aces: %.2f' % ace0_win_chance + '%\n')
stat_file.write('Chance of winning with 1 ace: %.2f' % ace1_win_chance + '%\n')
stat_file.write('Chance of winning with 2 aces: %.2f' % ace2_win_chance + '%\n')
stat_file.write('Chance of winning with 3 aces: %.2f' % ace3_win_chance + '%\n')
stat_file.write('Chance of winning with 4 aces: %.2f' % ace4_win_chance + '%\n\n')
stat_file.write('Mean number of wars per game: ' + str(np.mean(wars_per_game)) + '\n')
stat_file.write('Median number of wars per game: ' + str(np.median(wars_per_game)) + '\n')
stat_file.write('Mode number of wars per game: ' + str(stat.mode(wars_per_game)) + '\n')
stat_file.write('Max number of wars in a game: ' +  str(max(wars_per_game)) + '\n\n')
stat_file.close()

#set plot color for all plots
plot_color = 'tomato'

#plots histogram of average win values
fig = plot.figure()
plot.title('Number of Wins vs Initial Average Card Value')
plot.xlabel('Initial Average Card Value')
plot.ylabel('Number of Wins')
plot.xlim([4.5, 11.5])
plot.hist(win_means, bins=np.arange(4.5, 11.7, 0.2), color = plot_color)
plot.grid(axis='y')
fig.tight_layout()
plot.savefig('average_initial_card_value_histogram.png')

#plots histogram of number of wars per game
fig = plot.figure()
plot.title('Number of Games')
plot.xlabel('Number of Wars')
plot.ylabel('Occurences of the Number of Wars')
plot.xlim(-1, 100)
plot.bar(war_ct_complete_values, war_ct_complete_counts, color = plot_color)
plot.grid()
fig.tight_layout()
plot.savefig('wars_per_game_histogram.png')

#plots percent chance of winning vs initial averge card value
fig = plot.figure()
plot.title('Percent Chance of Winning vs Initial Average Card Value')
plot.xlabel('Initial Average Card Value')
plot.ylabel('Percent Chance of Winning [%]')
plot.scatter(bin_percentages.keys(), bin_percentages.values(), color = plot_color)
plot.plot(bin_percentages.keys(), bin_percentages.values(), color = plot_color)
plot.xticks(range(len(bin_percentages.keys())), rounded_bin_edges,rotation = 'vertical')
plot.grid()
fig.tight_layout()
plot.savefig('win_chance_vs_initial_average_card_value.png')

#plots percent chance of winning vs the number of aces dealt
fig = plot.figure()
plot.title('Percent Chance of Winning vs Number of Aces Dealt')
plot.xlabel('Number of Aces Dealt')
plot.ylabel('Percent Chance of Winning [%]')
plot.bar([0,1,2,3,4], ace_win_chance, color = plot_color)
plot.grid(axis='y')
fig.tight_layout()
plot.savefig('win_chance_vs_number_of_aces_dealt.png')

#plots the change in percent chance of winning per war vs initial average card value
fig = plot.figure()
plot.title('Change in Percent Chance of Winning Per War\nvs Initial Average Card Value')
plot.xlabel('Initial Average Card Value')
plot.ylabel('Change in Percent Chance\nof Winning Per War [%]')
plot.scatter(ordered_bin_keys, bin_slopes, color = plot_color)
plot.plot(ordered_bin_keys, bin_slopes, color = plot_color)
plot.xticks(range(len(bin_percentages.keys())), rounded_bin_edges, rotation = 'vertical')
plot.axhline(0, color = 'k')
plot.grid()
fig.tight_layout()
plot.savefig('change_in_win_change_per_war_vs_average_initial_card_value.png')

#plots the change in percent chance of winning per war vs number of aces dealt
fig = plot.figure()
plot.title('Change in Percent Chance of Winning Per War\nvs Number of Aces Dealt')
plot.xlabel('Number of Aces Dealt')
plot.ylabel('Change in Percent Chance\nof Winning Per War [%]')
plot.bar([0,1,2,3,4], ace_slopes, color = plot_color)
plot.axhline(0, color = 'k')
plot.grid(axis='y')
fig.tight_layout()
plot.savefig('change_in_win_chance_per_war_vs_number_of_aces_dealt.png')