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

from pickle import TRUE
import sys
from FisherHelper import FishHelper
from FisherClass import Fisher
from coinclicker import CoinClicker
from CharacterKiller import WantonNihilist

def testing(helper : FishHelper, game_dimensions : dict[str, any]):
    
    testgrab = helper.grab_screen(TRUE, game_dimensions)
    helper.save_picture(123, testgrab)

    return

def main(monitor = None):

    helper = FishHelper()

    print("For 15 seconds, program is now searching for Torchlight window")

    game_dimensions = helper.setup_game_screen(monitor)

    if game_dimensions is None:
        print("Program was not able to find Torchlight within 15 seconds. Exiting")
        sys.exit(0)

    print("Allright, Torchlight has been found. What do?\n1. Fish\n2. Click 4 gold\n3. Killman \n4. Exit")
    while True:
        val = input()
        try:
            val = int(val)
        except:
            print("Wrong input, input only a value between 1-3")
        if val in range (1,6):
            break;
        else:
            print("Wrong input, input a value between 1-3")

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
    if val == 5:
        testing(helper, game_dimensions)

    print("Control was returned to main, exiting the program.")

    sys.exit(0)

if __name__ == '__main__':
    main()