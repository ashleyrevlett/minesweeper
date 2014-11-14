import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

stat_list = list()

class Stat():
    def __init__(self, trial, score, win):
        self.trial = trial
        self.score = score
        self.win = win

def add_stat(Stat):
    stat_list.append(Stat)

def plot_stats(game_num, rows, cols, mines):

    idx = list(range(len(stat_list)))
    winners = list()
    losers = list()
    scores = list()

    for elem in stat_list:
        scores.append(elem.score)
        if elem.win == True:
            winners.append(elem)
        else:
            losers.append(elem)

    for i in idx:
        if stat_list[i].win == True:
            print "this one won"
            plt.bar(i, stat_list[i].score, color='b')

        else:
            print "this one lost"
            plt.bar(i, stat_list[i].score, color='r')

    plt.axis([0, game_num, 0, (rows * cols) - mines])
    plt.show()


