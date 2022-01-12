#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      anrik
#
# Created:     11-12-2021
# Copyright:   (c) anrik 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
from FisherHelper import FishHelper
from FisherClass import Fisher
from coinclicker import CoinClicker

def main(monitor = None):

    helper = FishHelper()

    print("For 15 seconds, program is now searching for Torchlight window")

    game_dimensions = helper.setup_game_screen(monitor)

    if game_dimensions is None:
        sys.exit("Program was not able to find Torchlight within 15 seconds. Exiting")

##    print("Allright, Torchlight has been found. What do?\n1. Fish\n2. Click 4 gold\n3. Exit")
##    while True:
##        val = input()
##        try:
##            val = int(val)
##        except:
##            print("Wrong input, input only a value between 1-3")
##        if val in range (1,3):
##            break;
##        else:
##            print("Wrong input, input a value between 1-3")

    val = 2
    mode = None

    if val == 1:
        fishman = Fisher(game_dimensions)
        fishman.go_fish()
        mode = fishman
    if val == 2:
        clickman = CoinClicker(game_dimensions)
        clickman.make_money()
        mode = clickman

##    if mode is not None and mode is not CoinClicker:
##        print("Program is exiting. Here are the final stats.")
##        stat_dict = mode.print_some_stats(mode.stat_dict, round(time() - deadline))
##    else:
##        print("Program exiting. Have fun achievementing")

    sys.exit()

if __name__ == '__main__':
    main()
