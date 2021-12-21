#-------------------------------------------------------------------------------
# Name:        FisherClass
# Purpose:
#
# Author:      anrik
#
# Created:     15-12-2021
# Copyright:   (c) anrik 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from FisherHelper import FishHelper
import cv2
import random
import pyautogui
import sys
from pathlib import Path
from time import time,sleep

class Fisher(FishHelper):
## Variables needed to perform fishing
    _needle_hole = cv2.imread("needle_holetime.png")
    _needle_fishbutton = cv2.imread("needle_fishbutton1.png")
    _needle_nothing = cv2.imread("needle_nothing.png")
    _needle_oktime = cv2.imread("needle_oktime.png")

    #Setup folders for saving needles
    _fail_folder = Path.cwd()
    _win_folder = f"{_fail_folder}/Pictures of wins/"
    _fail_folder = f"{_fail_folder}/Pictures of fails/"

    _win_needles = []
    _fail_needles = []

    stat_dict = {
        "total_fish_caught" : 0,
        "time_in_lottery": 0,
        "lottery_attempts": 0,
        "attempts": 0,
        "recent_fish": 0,
        "recent_fails" :0,
        "highest_perf" : 0
        }

    def __init__(self, game_dimensions):
        self._game_dimensions = game_dimensions
        FishHelper.__init__(self)

## Variables needed to perform fishing

    def go_fish(self):

        inside_dimensions = None
        deadline = time()
        while inside_dimensions is None:
            inside_dimensions = self.find_initial_fishing_hole(self._game_dimensions,self._needle_hole,self._needle_fishbutton)
            result = self.get_matchtemplate_results(self.grab_screen(True,dimensions = self._game_dimensions),self._needle_fishbutton)
            temp = result["max_loc"]
            x_offset = temp[0] + self._game_dimensions["left"] -115
            y_offset = temp[1] + self._game_dimensions["top"] -115
            if time() - deadline > 15:
                sys.exit("Program did not find the initial fishing hole within 15 seconds. Exiting.")
        ## necessary for "optimisation"
        ## Variables for managing the program state
        deadline = time()
        state = self.state_decide(clean_screen_img=self.grab_screen(True,dimensions=self._game_dimensions),threshold=0.9, one = self._needle_hole, two = self._needle_oktime, three = self._needle_fishbutton)
        fish_wins = 0
        fish_fails = 0
        min_wait = 4
        max_wait = 12

        time_for_stats = False
        fish_deadline = 0
        threshold_nudge = 0.005
        win_stats = []
        ## Variables for managing the program state

        while self._time_to_fish: #or time() - deadline < 120:
                sleep(0.15) #naive attempt to limit amount of calculation with ~60fps
                # states are 1 (fish), 2 (ok) , 3 (hole), 0 for state find
                if state == 0:
                    fresh_screen = self.grab_screen(True, dimensions=self._game_dimensions)
                    state = self.state_decide(clean_screen_img=fresh_screen, threshold = 0.86, one = self._needle_hole, two = self._needle_oktime,three = self._needle_fishbutton)
##                    if time_for_stats:
##                        self.stat_dict = print_some_stats(self.stat_dict)
##                        time_for_stats = False  ---------------------> move this to outside the class and handle program execution there
##                        if self.stat_dict["total_fish_caught"] > 105:
##                            _time_to_fish = False
                #fishing logic
                if state == 1: # this could live in its own function, but needs many globals :(
                    have_not_clicked = True
                    time_to_click = False
                    while have_not_clicked and self._time_to_fish:
                        if len(self._win_needles) < 1:

                            click_time = random.randint(min_wait,max_wait)
                            print(f"Fishing lottery started. Waiting for {click_time} seconds")
                            sleep(click_time)
                            time_to_click = True
                            #when its time to click, check if there's a high chance of a failpic
                            click_screen = self.grab_screen(False,inside_dimensions)
                            clean_screen = click_screen[:,:,:3]
                            result = self.get_matchtemplate_results(clean_screen,self._needle_fishbutton)
                            if len(self._fail_needles) > 1:
                                for needle in self._fail_needles:
                                    if self.find_item_on_screen(needle,0.945,screen_grab=clean_screen):
                                        time_to_click = False
                                        print("A click was rejected due to being too similar to a earlier failure.")
                                        break
                            if time_to_click:
                                center = self.get_center(result["max_loc"], self._needle_fishbutton)
                                pyautogui.click(center[0] + x_offset, center[1] + y_offset)
                                sleep(1.5)
                                self.stat_dict["lottery_attempts"] += 1
                                self.stat_dict["attempts"] +=1
                                if self.stat_dict["attempts"] % 10 == 0:
                                    time_for_stats = True
                                have_not_clicked = False
                                if len(self._fail_needles) > 1:
                                    min_wait = 2
                                    max_wait = 7
                                else:
                                    min_wait = 5
                                    max_wait = 15
                            else:
                                min_wait = 0
                                max_wait = 3
                        else:
                            if self.stat_dict["time_in_lottery"] == 0:
                                self.stat_dict["time_in_lottery"] = time() - deadline
                                fish_deadline = time()
                                threshold_nudge = 0.005
                            click_screen = self.grab_screen(False,inside_dimensions)
                            clean_screen = click_screen[:,:,:3]
                            result = self.get_matchtemplate_results(clean_screen,self._needle_fishbutton)
                            if time() - fish_deadline > 30:
                                threshold_nudge += threshold_nudge

                            stat_track = 0
                            for needle in self._win_needles:
                                if self.find_item_on_screen(needle,0.985-threshold_nudge,screen_grab=clean_screen):
                                    time_to_click = True
                                    break
                                stat_track +=1

                            for needle in self._fail_needles:
                                if self.find_item_on_screen(needle,0.96,screen_grab=clean_screen):
                                    time_to_click = False
                                    stat_track = None
                                    break

                            if time_to_click:
                                center = self.get_center(result["max_loc"], self._needle_fishbutton)
                                pyautogui.click(center[0] + x_offset, center[1] + y_offset)
                                sleep(1.5)
                                fish_deadline = time()
                                threshold_nudge = 0.005
                                self.stat_dict["attempts"] +=1
                                if self.stat_dict["attempts"] % 10 == 0:
                                    time_for_stats = True
                                #now send the click_screen to the OK function
                                have_not_clicked = False
                    state = 0

                if state == 2:
                    if self.find_item_on_screen(self._needle_nothing,0.95, dimensions=self._game_dimensions):
                        #it was a fail, save the image
                        if fish_fails < 20: #fully arbitrary number
                            saved_image = self.save_picture(fish_fails, click_screen, folder=self._fail_folder)
                            self._fail_needles.append(cv2.imread(saved_image))
                            fish_fails += 1
        ##              else:
        ##                    fail_needles.pop(0)
        ##                    fish_fails = 0
                        self.stat_dict["recent_fails"] += 1
                    else:
                        #it was a win, save the image as win
                        if fish_wins < 1 : #fully arbitrary number
                            saved_image = self.save_picture(fish_wins, click_screen, folder=self._win_folder)
                            if fish_wins < 1:
                                self._win_needles.append(cv2.imread(saved_image))
                                fish_wins += 1
        ##                    elif threshold_nudge > 4 * threshold_nudge:
        ##                        __win_needles.append(cv2.imread(saved_image))
        ##                        fish_wins += 1
                        self.stat_dict["recent_fish"] += 1
                        self.stat_dict["total_fish_caught"] +=1
                    if self.find_and_click(self._game_dimensions,self._needle_oktime,0.9):
                        sleep(1.5)
                        state = 0

                if state == 3:
                    if self.find_and_click(self._game_dimensions,self._needle_hole, 0.9):
                        sleep(1.5)
                        state = 0


