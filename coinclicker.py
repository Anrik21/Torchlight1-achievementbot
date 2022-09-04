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

from colorsys import ONE_SIXTH
import cv2, pyautogui, keyboard, pytesseract
from time import time,sleep
from FisherHelper import FishHelper
from keyboard import add_hotkey

class CoinClicker(FishHelper):
    _needle_buy = cv2.imread("needle_buy.png")
    _needle_sell = cv2.imread("needle_sell.png")
    _needle_shopping = cv2.imread("needle_shopping.png")
    _needle_retry_shop = cv2.imread("needle_try_reset_shopping.png")

    _leftside_dimensions = None
    _rightside_dimensions = None
    
    _time_for_clicking = True

    stat_dict = {"best_perf" : 0,
    "clicks" : 0,
    "starting_gold" : 0,
    "current_gold" : 0,
    "total_gold_made" : 0
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

    def on_space(self):
        self._time_for_clicking = False

    def click_then_sell(self, click_dur):
        keyboard.press('shift')
        sleep(click_dur)
        pyautogui.click(x = self._x_buy_pos, y = self._y_buy_pos)
        sleep(click_dur)
        pyautogui.click(x = self._x_sell_pos, y = self._y_sell_pos)
        keyboard.release('shift')
        self.stat_dict["clicks"] += 1

    def buy_max_then_sell(self, click_dur):
        
        keyboard.press('shift')

        pyautogui.moveTo(x = self._x_buy_pos, y = self._y_buy_pos, duration=click_dur*2)

        # 210 clicks to fill an inventory
        for i in range(0, 210):
            if (self._time_for_clicking):
                pyautogui.click(x = self._x_buy_pos, y = self._y_buy_pos)

        for j in range(0, 3):
            pyautogui.moveTo(x = self._x_sell_pos, y = self._y_sell_pos + (j * 80), duration=click_dur*2)
            for i in range(0, 8):
                if (self._time_for_clicking):
                    pyautogui.click(x = self._x_sell_pos + (i * 47), y = self._y_sell_pos + (j * 80), duration = click_dur)
                    if i == 7:
                        pyautogui.click(x = self._x_sell_pos + (i * 47), y = self._y_sell_pos + (j * 80), duration = click_dur)

        keyboard.release('shift')
        self.stat_dict["clicks"] += 210
            

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
        clicks_before_break = 210
        iterations = 0
        threshold = { 1 : 0.7 , 2 : 0.7}
        
        add_hotkey('space', self.on_space)

        while self._time_for_clicking:

            if state == 0:
                clean_img = self.grab_screen(True, dimensions = self._game_dimensions)
                if regular_state_check:
                    state = self.state_decide(clean_screen_img=clean_img, threshold=threshold, one = self._needle_retry_shop, two = self._needle_shopping)
                else:
                    state = 3
                    regular_state_check = True

            if state == 1:
                print("Looking for shop")
                if self.find_and_click(self._game_dimensions,self._needle_retry_shop,0.75):
                    sleep(1.5)
                    state = 0

            if state == 2:
                print("Double checking that i'm in the right state.")
                state = self.state_decide(clean_screen_img=clean_img, threshold=threshold, one = self._needle_retry_shop, two = self._needle_shopping)
                if state != 2:
                    print("Stateconfusion, returning to statechecker to try and reset.")
                    state = 0
                    regular_state_check = True
                elif self.stat_dict["starting_gold"]  == 0:
                    self.stat_dict["starting_gold"] = self.get_gold_number()
                    print("Starting to click with {} starting gold.".format(self.stat_dict["starting_gold"]))

                self.buy_max_then_sell(click_dur)

                if self.stat_dict["clicks"] > clicks_before_break:
                    clicks = self.stat_dict["clicks"]
                    print(f"Clicking has been done {clicks} times, time for evaluation")
                    iterations += 1
                    regular_state_check = False
                    state = 0

            if state == 3:
                get_gold = self.get_gold_number()
                if get_gold is not None:
                    if self.stat_dict["current_gold"] != 0:
                        last_curr_gold = self.stat_dict["current_gold"]
                        self.stat_dict["current_gold"] = get_gold
                        curr_perf = get_gold - last_curr_gold
                    else:
                        self.stat_dict["current_gold"] = get_gold
                        curr_perf = get_gold - self.stat_dict["starting_gold"]
                    
                    self.stat_dict["total_gold_made"] += curr_perf
                    print("\n####################################")
                    print("Starting gold was {}\nCurrent gold {}\nGold made this iteration {}".format(self.stat_dict["starting_gold"], self.stat_dict["current_gold"], curr_perf))
                    print("Total gold made {}".format(self.stat_dict["total_gold_made"]))

                    #Assume that clicks were perfect & also allow for a miss of 10x
                    expected_perf = (210 * 6) - 60
                    
                    if curr_perf < expected_perf:
                        print(f"Performance is {curr_perf}, below the expected performance of {expected_perf}.")
                        self.stat_dict["best_perf"] -= 1
                    else:
                        print(f"Performance is {curr_perf}, above the expected performance of {expected_perf}.")
                        self.stat_dict["best_perf"] += 1

                    if self.stat_dict["best_perf"] > 4:
                        print("Performance of 4 last attempts was over the expected. Increasing the clickspeed and interval length.")
                        clicks_before_break += 210
                        self.stat_dict["best_perf"] = 0
                        if click_dur - 0.01 != 0:
                            click_dur -= 0.01

                    if self.stat_dict["best_perf"] < -2:
                        print("Performance has been poor for 2 iterations. Decreasing the clickspeed and resetting interval length.")
                        clicks_before_break = 100
                        self.stat_dict["best_perf"] = 0
                        click_dur += 0.01 

                    print("####################################\n")

                else:
                    print(f"Program failed to read value on screen, will retry in {clicks_before_break} clicks.")

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

