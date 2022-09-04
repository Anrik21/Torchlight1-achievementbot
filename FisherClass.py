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

from ast import excepthandler
from asyncio.log import logger
from email.message import EmailMessage
from pydoc import Helper
from tkinter import LAST
from FisherHelper import FishHelper
import cv2
import random
import pyautogui
import sys
from pathlib import Path
from keyboard import add_hotkey
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
    _time_to_fish = True

    _win_needles = {}
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

    def on_space(self):
        self._time_to_fish = False

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
            self.save_picture("testpic of screen", self.grab_screen(True, dimensions=self._game_dimensions))
            if time() - deadline > 15:
                print("Program did not find the initial fishing hole within 15 seconds. Exiting.")
                sys.exit(0)
        ## necessary for "optimisation"
        add_hotkey('space',self.on_space)

        ## Variables for managing the program state
        deadline = time()
        fish_wins = 0
        fish_fails = 0
        min_wait = 4
        max_wait = 12
        last_state = {}
        state_threshold = 0.75
        state_text = {0 : "looking for state", 1 : "fishing", 2: "trying to click OK", 3: "looking for fishing hole"}
        all_state_thresholds = { 1 : state_threshold, 2 : state_threshold, 3 : state_threshold  }

        state = self.state_decide(clean_screen_img=self.grab_screen(True,dimensions=self._game_dimensions),
                                                threshold=all_state_thresholds, 
                                                one = self._needle_fishbutton, two = self._needle_oktime, three = self._needle_hole)
        time_for_stats = False
        fish_deadline = 0
        threshold_nudge = 0.005
        win_stats = []
        time_before_giving_up = 300
        fishbutton_loc = ()
        ## Variables for managing the program state

        while self._time_to_fish and time() - deadline < time_before_giving_up:
                sleep(0.15) #naive attempt to limit amount of calculation with ~60fps
                # states are 1 (fish), 2 (ok) , 3 (hole), 0 for state find
                if state == 0:
                    sleep(0.3)
                    fresh_screen = self.grab_screen(True, dimensions=self._game_dimensions)

                    # To encourage a different state than last time, nudge the threshold slightly.
                    for key, val in last_state.items():
                        all_state_thresholds[key] += val

                    print("\n##########")
                    print("Statefinding")
                    state = self.state_decide(clean_screen_img=fresh_screen, threshold=all_state_thresholds, one = self._needle_fishbutton, two = self._needle_oktime,three = self._needle_hole)
                    print("I think I'm {0}".format(state_text[state]))
                    print("##########\n")

                    # After a state has been picked, clean up the nudging
                    for key, val in all_state_thresholds.items():
                        all_state_thresholds[key] = state_threshold

                    if state in last_state:
                        del last_state[state]
                    elif state != 0:
                        last_state[state] = 0.1
                        
                #fishing logic
                if state == 1: # this could live in its own function, but needs many globals :(
                    have_not_clicked = True
                    time_to_click = False
                    
                    if not fishbutton_loc:
                        tempResult= self.get_matchtemplate_results(self.grab_screen(True, inside_dimensions),self._needle_fishbutton)
                        fishbutton_loc = self.get_center(tempResult["max_loc"], self._needle_fishbutton)
                    pyautogui.moveTo(fishbutton_loc[0] + x_offset +40, fishbutton_loc[1] + y_offset)

                    risk = 0

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
                                    if self.find_item_on_screen(needle,0.90+risk,screen_grab=clean_screen):
                                        time_to_click = False
                                        print("A click was rejected due to being too similar to a earlier failure.")
                                        break
                            if time_to_click:
                                print("It's time to click. Attempting to find and click button.")
                                click_deadline = time()
                                while self.find_item_on_screen(self._needle_fishbutton, 0.7 , inside_dimensions):
                                    pyautogui.click(fishbutton_loc[0] + x_offset, fishbutton_loc[1] + y_offset, duration=0.1)
                                    sleep(0.5)
                                    if time() - click_deadline > 30:
                                        print("Failed to verify that a successful click was done. Exiting fishing state")
                                        state = 0
                                        break;

                                if state != 0:
                                    risk = 0
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
                                risk += 0.001
                                min_wait = 0
                                max_wait = 3
                        else:
                            sleep(0.15)
                            if self.stat_dict["time_in_lottery"] == 0:
                                self.stat_dict["time_in_lottery"] = time() - deadline
                                click_deadline = time()
                                print("Lottery done, now comparing winneedle.")
                                risk = 0

                            click_screen = self.grab_screen(False,inside_dimensions)
                            clean_screen = click_screen[:,:,:3]
                            result = self.get_matchtemplate_results(clean_screen,self._needle_fishbutton)
                            
                            for i in self._win_needles:
                                if self.find_item_on_screen(self._win_needles[i]["image"] ,0.88 - risk,screen_grab=clean_screen):
                                    time_to_click = True
                                    most_recent_winner = i
                                    print("I think i found the time to click.")
                                    break

                            if time_to_click:
                                for needle in self._fail_needles:
                                    if self.find_item_on_screen(needle,0.94 + risk,screen_grab=clean_screen):
                                        time_to_click = False
                                        print("... but still pretty likely to have a fail, click stopped.")
                                        break

                            if not time_to_click and time() - click_deadline > 45:
                                if risk == 0:
                                    print("Needle strategy is being slow, increasing risk every cycle.")
                                risk += 0.0001

                            if time_to_click:

                                print("It's time to click. Attempting to find and click button.")
                                risk = 0
                                click_deadline = time()
                                while self.find_item_on_screen(self._needle_fishbutton, 0.7 , inside_dimensions):
                                    pyautogui.click(fishbutton_loc[0] + x_offset, fishbutton_loc[1] + y_offset, duration=0.1)
                                    sleep(0.5)
                                    if time() - click_deadline > 15:
                                        print("Failed to verify that a successful click was done. Exiting fishing state")
                                        state = 0
                                        break;

                                print("Clicked. Checking state")
                                sleep(4)
                                state_check = self.state_decide(clean_screen_img=self.grab_screen(True,dimensions=self._game_dimensions),
                                                threshold=all_state_thresholds, 
                                                one = self._needle_fishbutton, two = self._needle_oktime, three = self._needle_hole)
                                if state_check != 2:
                                    logger.debug("Failed to click while fishing")
                                    print("Click fucked up. Adding to log. Deadline not reset, program will close in {} seconds".format(round(time_before_giving_up - (time()-deadline))))
                                    have_not_clicked = False
                                else:
                                    print("Click seemed to work")
                                    self.stat_dict["attempts"] +=1
                                    if self.stat_dict["attempts"] % 10 == 0:
                                        time_for_stats = True
                                    #now send the click_screen to the OK function
                                    have_not_clicked = False
                    
                    try:
                        state = state_check
                    except:
                        state = 0

                if state == 2:
                    if self.find_item_on_screen(self._needle_nothing,0.85, dimensions=self._game_dimensions):
                        #it was a fail, save the image
                        print("Fishing was a fail.")
                        if len(self._fail_needles) < 20:
                            saved_image = self.save_picture(fish_fails, click_screen, folder=self._fail_folder)
                            self._fail_needles.append(cv2.imread(saved_image))
                            fish_fails += 1
                        else:
                            print("There are more than 20 fails, removing the 10 oldest ones.")
                            for i in range(0, 10):
                                self._fail_needles.pop(0)
                            
                        self.stat_dict["recent_fails"] += 1
                    else:
                        #it was a win, save the image as win
                        print("Fishing was a win.")
                        if len(self._win_needles) < 4 : 
                            saved_image = self.save_picture(fish_wins, click_screen, folder=self._win_folder)
                            self._win_needles[fish_wins] = {"wins" : 1 , "image" : cv2.imread(saved_image) } 
                            fish_wins += 1

                        try:
                            self._win_needles[most_recent_winner]["wins"] += 1
                        except:
                            logger.debug("Most recent winner not assigned, caused exception.", self._win_needles)

                        if self.stat_dict["recent_fails"] > 2 and len(self._win_needles) > 2:
                            print("There were recently more than 2 failures in a row. Removing the oldest win picture.")
                            lowest = 0
                            index_to_remove = 0
                            for i in self._win_needles:
                                if lowest < self._win_needles[i]["wins"]:
                                    lowest = self._win_needles[i]["wins"]
                                    index_to_remove = i
                            print ("Removing {} due to having the lowest wins.".format(self._win_needles[i]))
                            self._win_needles.pop(index_to_remove)

                        self.stat_dict["recent_fails"] = 0
                        self.stat_dict["recent_fish"] += 1
                        self.stat_dict["total_fish_caught"] +=1
                        deadline = time()

                    while self.find_and_click(self._game_dimensions,self._needle_oktime,0.9):
                        sleep(0.5)
                    
                    state = 0

                if state == 3:
                    if self.find_and_click(self._game_dimensions,self._needle_hole, 0.9):
                        sleep(1)
                    
                    state = 0

        logger.debug( "Finished fishing. Semistats.")
        try:
            logger.debug( "Attempts: {}".format(self.stat_dict["attempts"]))
            logger.debug( "Wins: {}".format(self.stat_dict["total_fish_caught"]))
        except:
            logger.debug("No attempts or wins to log.")
        
        logger.debug("Stats for the final win needles.")    
        try:
            for i in self._win_needles:
                logger.debug(f"Needle no: {i}. Wins: " + str(self._win_needles[i]["wins"]))
        except:
            logger.debug("No stats to print (or there were and an exception was thrown)")

        return



