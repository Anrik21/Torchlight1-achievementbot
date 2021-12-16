#-------------------------------------------------------------------------------
# Name:        CoinClicker
# Purpose:     This module only works if you have a specific mod installed in torchlight.
#              This mod abuses the fact that an item is sold for -6 gold,
#              so this tries to click on that item a lot, then sell it back to repeat it.
#              Mod folder is simply called merchant, got the mod from here:
#              https://www.torchlightfansite.com/mod_downloads/compilations-tl1/download-742-sin-mod-pack-1-01-a.html
#
# Author:      anrik
#
# Created:     15-12-2021
# Copyright:   (c) anrik 2021
#
#-------------------------------------------------------------------------------

import cv2, pyautogui, keyboard
from time import time,sleep
from FisherHelper import FishHelper

class CoinClicker(FishHelper):
    _needle_buy = cv2.imread("needle_buy.png")
    _needle_sell = cv2.imread("needle_sell.png")
    _needle_shopping = cv2.imread("needle_shopping.png")
    _needle_retry_shopping = cv2.imread("needle_try_reset_shopping.png")

    _leftside_dimensions = None
    _rightside_dimensions = None

    def __init__(self, game_dimensions):
        FishHelper.__init__(self)

        self._game_dimensions = game_dimensions.copy()

        self._leftside_dimensions = game_dimensions.copy()
        self._leftside_dimensions["width"] = 220
        self._leftside_dimensions["height"] = 390

        self._rightside_dimensions = game_dimensions.copy()
        self._rightside_dimensions["left"] += 845
        self._rightside_dimensions["top"] += 660
        self._rightside_dimensions["width"] = 147
        self._rightside_dimensions["height"] = 127

        self._x_buy_pos = 181 + game_dimensions["left"]
        self._y_buy_pos = 346 + game_dimensions["top"]

        self._x_sell_pos = 892 + game_dimensions["left"]
        self._y_sell_pos = 740 + game_dimensions["top"]

    def make_money(self):
        '''
        Clicks on the screen! If your game is set to the correct resolution and you have the same mods,
        this function clicks in the places of an item that costs -6 gold, and then tries to sell it.

        Further devs: add image recognition and have it self tune the framerate (now it sometimes "misses" clicks.
        '''
        clicks = 0
        state = 0
        deadline = None
        while self._time_to_fish:
            if clicks % 100 == 0:
                if self.find_item_on_screen(self._needle_shopping, 0.75,dimensions=self._game_dimensions):
                    state = 2
                    if clicks == 0:
                        print("Correctly identified the shopping window, starting to click")
                    else:
                        print(f"I've sold the bottle {clicks} times. Here's to {clicks} more clicks!")
                else:
                    if state == 0:
                        print("Did not find shopping menu, looking for dude to click for 15 seconds.")
                        if deadline is None:
                            deadline = time()
                        state = 1
                        if time() - deadline > 15:
                            self._time_to_fish = False

            if state == 1:
                if self.find_and_click(self._game_dimensions,self._needle_retry_shopping,0.75):
                    print("Seems like i found him, waiting and trying to affirm shopping status.")
                    sleep(1.5)
                    state = 0

            if state == 2:
                keyboard.press('shift')
                pyautogui.click(x = self._x_buy_pos, y = self._y_buy_pos, clicks=2 , duration=0.1)
                pyautogui.click(x = self._x_sell_pos, y = self._y_sell_pos, clicks=3, duration=0.1)
                keyboard.release('shift')
                clicks += 2