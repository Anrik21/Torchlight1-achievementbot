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
from CharacterKiller import WantonNihilist

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

    val = 3

    if val == 1:
        fishman = Fisher(game_dimensions)
        fishman.go_fish()
    if val == 2:
        clickman = CoinClicker(game_dimensions)
        clickman.make_money()
    if val == 3: ## Potentially add a "how many deaths do you want?"
        killman = WantonNihilist(game_dimensions)
        killman.go_die()
    if val == 4:
        sys.exit()

    sys.exit()

if __name__ == '__main__':
    main()
