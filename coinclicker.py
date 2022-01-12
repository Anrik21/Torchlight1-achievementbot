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

import cv2, pyautogui, keyboard, pytesseract
from time import time,sleep
from FisherHelper import FishHelper

class CoinClicker(FishHelper):
    _needle_buy = cv2.imread("needle_buy.png")
    _needle_sell = cv2.imread("needle_sell.png")
    _needle_shopping = cv2.imread("needle_shopping.png")
    _needle_retry_shop = cv2.imread("needle_try_reset_shopping.png")

    _leftside_dimensions = None
    _rightside_dimensions = None

    stat_dict = {"best_perf" : 0.7,
    "clicks" : 0,
    "starting_gold" : 0,
    "current_gold" : 0
    }

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

        self._money_dimensions = game_dimensions.copy()
        self._money_dimensions["left"] += 953
        self._money_dimensions["top"] += 929
        self._money_dimensions["width"] = 220
        self._money_dimensions["height"] = 45

        self._x_buy_pos = 181 + game_dimensions["left"]
        self._y_buy_pos = 346 + game_dimensions["top"]

        self._x_sell_pos = 892 + game_dimensions["left"]
        self._y_sell_pos = 740 + game_dimensions["top"]

    def make_money(self, money_to_make = None):
        '''
        Clicks on the screen! If your game is set to the correct resolution and you have the same mods,
        this function clicks in the places of an item that costs -6 gold, and then tries to sell it.

        Further devs: add image recognition and have it self tune the framerate (now it sometimes "misses" clicks.
        '''
        # every 500*performance clicks, review performance. Performance is clicks/hits
        # starting like this: want to save/load this between sessions
        clicks = 0
        state = 0
        # Version 1: just go with either increasing/decreasing this depending on performance
        # Version later: try to change them individually or experiment
        click_dur = 0.1
        # States??
        # 1. Look for merchant. 2. Do click (leave by itself after N clicks) 3. Do the number magic
        deadline = None
        regular_state_check = True
        modulo_var = 100

        while self._time_to_fish:

            if state == 0:
                clean_img = self.grab_screen(True, dimensions = self._game_dimensions)
                if regular_state_check:
                    state = self.state_decide(clean_screen_img=clean_img, threshold=0.82, one = self._needle_retry_shop, two = self._needle_shopping)
                else:
                    state = 3
                    regular_state_check = True

            if state == 1:
                if self.find_and_click(self._game_dimensions,self._needle_retry_shop,0.75):
                    sleep(1.5)
                    state = 0

            if state == 2:
                if self.stat_dict["starting_gold"] == 0:
                    self.stat_dict["starting_gold"] = self.get_gold_number()
                    print("Starting to click with {} starting gold.".format(self.stat_dict["starting_gold"]))
                keyboard.press('shift')
                sleep(click_dur)
                pyautogui.click(x = self._x_buy_pos, y = self._y_buy_pos)
                sleep(click_dur)
                pyautogui.click(x = self._x_sell_pos, y = self._y_sell_pos)
                keyboard.release('shift')
                self.stat_dict["clicks"] += 1
                if self.stat_dict["clicks"] % modulo_var == 0:
                    clicks = self.stat_dict["clicks"]
                    print(f"Clicking has been done {clicks} times, time for evaluation")
                    regular_state_check = False
                    state = 0

            if state == 3:
                get_gold = self.get_gold_number()
                if get_gold is not None:
                    if self.stat_dict["current_gold"] != 0:
                        last_curr_gold = self.stat_dict["current_gold"]
                        self.stat_dict["current_gold"] = get_gold
                        performance = curr_perf
                        curr_perf = self.stat_dict["current_gold"] - last_curr_gold
                    else:
                        self.stat_dict["current_gold"] = get_gold
                        curr_perf = self.stat_dict["current_gold"] - self.stat_dict["starting_gold"]
                        performance = self.stat_dict["best_perf"]

                    print("Starting gold was {}\nCurrent gold {}\nGold made {}".format(self.stat_dict["starting_gold"], self.stat_dict["current_gold"], curr_perf))
                    print(f"Clicks since last check: {modulo_var}")

                    curr_perf = curr_perf / 6
                    curr_perf = curr_perf / modulo_var

                    if curr_perf < performance:
                        print(f"Performance is {curr_perf}, below last performance of {performance}. Making clicking slower")
                        click_dur += 0.01
                    else:
                        print(f"Performance is {curr_perf}, above last performance of {performance}. Making clicking faster")
                        if click_dur - 0.01 != 0:
                            click_dur -= 0.01
                        self.stat_dict["best_perf"] = curr_perf

                    if curr_perf > .95:
                        modulo_var += 100
                else:
                    print(f"Program failed to read value on screen, will retry in {modulo_var} clicks.")

                state = 0

            if money_to_make is not None:
                money_made = self.stat_dict["current_gold"] - self.stat_dict["starting_gold"]
                if money_made > money_to_make:
                    self._time_to_fish = False

    def get_gold_number(self):
        money_pic = self.grab_screen(False, dimensions = self._money_dimensions)
        text = self.get_text_from_money(money_pic)
        text = ''.join(filter(str.isdigit,text))

        try:
            text = int(text)
        except ValueError:
            text = None

        return text

    def get_text_from_money(self, non_cleaned_img):

        sleep(0.5)

        pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract\tesseract.exe"

        gray = cv2.cvtColor(non_cleaned_img, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY_INV)
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4,4))
        dilation = cv2.dilate(thresh1, rect_kernel, iterations=4)
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        text_image2 = non_cleaned_img.copy()

        output_text = ""
        id = 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

##            x -= 4
##            y -= 3
##            w += 2
            h -= 3

            rect = cv2.rectangle(text_image2, (x,y), (x+w,y+h),(0,255,255),1)

            cropped = text_image2[y:y+h,x:x+w]

            self.save_picture(id, cropped)

            output_text += pytesseract.image_to_string(cropped, config='--psm 8')
            id+=1

        #print(output_text)
        return output_text
