#-------------------------------------------------------------------------------
# Name:        FisherHelper
# Purpose:     Make code in fisher/achievement bot more manage-able.
#
# Author:      anrik
#
# Created:     15-12-2021
# Copyright:   (c) anrik 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import cv2
import sys
import pyautogui
import random
import keyboard
import numpy
import logging
from datetime import datetime
from pathlib import Path
from glob import glob
from mss import mss
from time import time, sleep

datetime_now = datetime.now().strftime("%d-%m-%Y__%H-%M-%S")
tempFileName = "achievelog{0}.log".format(datetime_now)
logging.basicConfig(format='%(levelname)s:%(message)s',filename=tempFileName, level=logging.DEBUG)
logging.info(f"{datetime_now} - Logging started")

class FishHelper():
    '''Contains helper functions to perform achievement tasks in torchlight'''

    def __init__(self):
        self._time_to_fish = True
        keyboard.add_hotkey('space',self.on_space)
        keyboard.add_hotkey('shift+space',self.on_space)

    def log_end(self):
        datetime_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        logging.info(f"{datetime_now} - Logging ended")

    def state_decide(self, clean_screen_img, threshold, **needles):
        '''
        This function takes N amount of states, an image to look for things in,
        a threshold (value betwen 0 & 1), as well as a collection of needles which
        will be attempted to be found in the image.

        If the threshold is met with any of the needles, the program will return an integer
        which is in the range of 1-N representing the needle which had the highest result in
        the comparison in the picture.

        If the threshold is not met, 0 will be returned, use that for the state to look for state.
        '''
        needle_results = []
        threshold_passed = False
        for key, needle in needles.items():
            result = self.get_matchtemplate_results(clean_screen_img, needle)
            needle_results.append(result["max_val"])

        for result in needle_results:
            if result > threshold:
                threshold_passed = True
                break

        state = 0
        comparer = 0
        if threshold_passed:
            for val in range (1, len(needles)+1):
                if needle_results[val-1] > comparer:
                    comparer = needle_results[val-1]
                    state = val
                    logging.info(f"Current highest val is {comparer}, with state {state}")

            return state
        else:
            logging.debug("Threshold not passed in state_decide")
            return 0

    def find_initial_fishing_hole(self,dimensions, hole_needle, fish_needle):
        self.find_and_click(dimensions, hole_needle, 0.9)
        sleep(1.5)
        #Doing a manual check to be set up "screen in screen" for smaller comparisons
        match_result = self.get_matchtemplate_results(self.grab_screen(True,dimensions),fish_needle)
        if match_result["max_val"] > .85:
            inside_dimensions = dimensions.copy()
            point_one = match_result["max_loc"]
            point_two = fish_needle.shape

            # 115 may look random but it's approx the size of the max sized fishcircle in the minigame at this resolution
            inside_dimensions = self.change_dimensions(inside_dimensions, (point_one[0]-115,point_one[1] -115), (point_two[0]+230,point_two[1]+230))
        else:
            inside_dimensions = None

        return inside_dimensions

    def find_item_on_screen(self,needle, threshold, dimensions = None, screen_grab = None):
        if screen_grab is None and dimensions is not None:
            screen_grab = self.grab_screen(True,dimensions)
        if screen_grab is None and dimensions is None:
            return false
        search = self.get_matchtemplate_results(screen_grab, needle)

        if search["max_val"] > threshold:
            return True
        return False

    def find_and_click(self,game_dimensions, needle, threshold):
        clean_source = self.grab_screen(True, game_dimensions)
        hole_search = self.get_matchtemplate_results(clean_source, needle)
        if hole_search["max_val"] > threshold:
            loc = self.get_center(hole_search["max_loc"], needle)
            pyautogui.click(x = loc[0] +game_dimensions["left"],y=loc[1]+game_dimensions["top"])
            return True
        return False

    def setup_game_screen(self,monitor):
        program_needle = cv2.imread("needle_torchprogram.png")
        find_game_timer = time()
        torch_found = False
        game_window = None
        if monitor is None:
            monitor = 1

        while time() - find_game_timer < 15 and not torch_found:
            scr_source = self.grab_screen(True,monitor=monitor)
            result_dict = self.get_matchtemplate_results(scr_source, program_needle)

            max_val = result_dict["max_val"]
            max_loc = result_dict["max_loc"]
            logging.debug(f"Max val is {max_val}")
            if max_val > .90:
                logging.info(f"Max val was higher than 90%, so I think I found it at...")
                logging.info(f"Max val: {max_val} Max loc: {max_loc}")
                with mss() as sct:
                    mon = sct.monitors[monitor]
                game_window = {
                    "left" : mon["left"] + max_loc[0],
                    "top" : mon["top"] + max_loc[1],
                    "width" : 1280,
                    "height" : 1024,
                    "mon" : monitor
                }
                torch_found = True
            else:
                logging.debug("Did not find it yet...")
            sleep(0.5)

        if not torch_found:
            logging.critical("Program window was not fun. Exiting.")

        return game_window

    def get_center(self,max_loc, needle):
        center = (max_loc[0] + round(needle.shape[1]/2), max_loc[1] + round(needle.shape[0]/2))

        return center

    def grab_screen(self,clean, dimensions = None, monitor = None ):

        if monitor is None and dimensions is None:
            with mss() as sct:
               region = sct.monitors[1]
               source = numpy.array(sct.grab(region))

        if monitor is not None and dimensions is None:
            with mss() as sct:
               source = numpy.array(sct.grab(sct.monitors[monitor]))

        if dimensions is not None:
            with mss() as sct:
                source = numpy.array(sct.grab(dimensions))

        if clean:
            source = source[:,:,:3]

        return source


    def change_dimensions(self,dimensions, point_one, point_two):
        '''
        Changes dimensions (a dict with 4 valuepairs: left, top, width & height)
        to the given points: top left will be point one, bottom right point two.
        '''
        dimensions["left"] += point_one[0]
        dimensions["top"] += point_one[1]
        dimensions["width"] = point_two[0]
        dimensions["height"] = point_two[1]

        return dimensions

    def get_matchtemplate_results(self,cleaned_source, needle):
        '''
        Takes a picture, a picture to look for inside the picture and returns
        a dictionary with min_val, max_val, min_loc, max_loc.
        Uses TM_CCOEFF_NORMED to look for picture.
        '''
        result = cv2.matchTemplate(cleaned_source,needle,cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        result_dict = {
        "min_val" : min_val,
        "max_val" : max_val,
        "min_loc" : min_loc,
        "max_loc" : max_loc
        }

        return result_dict

    def save_picture(self,pic_ID, picture, folder = None, point_one = None, point_two = None):
        '''
        Takes a number to append to the filename (which is PointPic{ID}), saves it at folder or just
        currentfolder/Saved_Images/ . You can add a rectangle to the saved picture by giving this
        two points.

        Returns the path to the created image.
        '''
        currentdir = Path.cwd()

        if folder is None:
            Path(f"{currentdir}/Saved Images").mkdir(exist_ok=True)
            output_path = f"{currentdir}/Saved Images/PointPic{pic_ID}.png"
        else:
            Path(f"{folder}").mkdir(exist_ok=True)
            output_path = f"{folder}/PointPic{pic_ID}.png"


        if point_one is not None and point_two is not none:
            cv2.rectangle(picture, point_one, point_two, (0,255,255), 2)

        attempt = cv2.imwrite(output_path, picture)

        if attempt:
            return output_path
        else:
            return None

    def print_some_stats(self,stat_dict, final = None):
        caught = stat_dict["total_fish_caught"]
        lottery_time = stat_dict["time_in_lottery"]
        lottery_attempts = stat_dict["lottery_attempts"]
        total_att = stat_dict["attempts"]
        recent_w = stat_dict["recent_fish"]
        recent_f = stat_dict["recent_fails"]
        performance = stat_dict["highest_perf"]

        if final is None:
            print("10 attempts have been done since last stat. Here's the programs stats.")

        if lottery_time == 0:
            print(f"Lottery is still ongoing. Current attempts in lottery {lottery_attempts}.")
        elif lottery_attempts >= total_att:
            lottery_time = round(lottery_time)
            print(f"Lottery took {lottery_attempts} and took {lottery_time} seconds.")
            stat_dict["time_in_lottery"] = lottery_time

        if final is not None:
            print(f"The total runtime of the program was {final} seconds.")
            lottery_time = round(lottery_time)
            print(f"Lottery took {lottery_attempts} attempts and took {lottery_time} seconds.")
            time_fishing = round(final-lottery_time)
            print(f"The rest of the operations were carried out for {time_fishing} seconds.")

        print(f"\nThe program has done {total_att} attempts and caught {caught} fish.")
        perf = round(caught/total_att,4)*100
        print(f"The programs stat is {perf}% fish rate.")
        if final is None:
            print(f"In the recent 10 attempts, there were {recent_w} catches and {recent_f} fails.")
            perf = round(recent_w/10,4)*100
            if perf > performance:
                print(f"With a performance of {perf}% it beats the last best of {performance}%.")
                stat_dict["highest_perf"] = perf
            else:
                print(f"With a performance of {perf}% it's worse than the last best of {performance}%.")
        else:
            print(f"The programs best 10 attempts had a {performance}% accuracy of fish.")

        stat_dict["recent_fish"] = 0
        stat_dict["recent_fails"] = 0

        return stat_dict

    def on_space(self):
        self._time_to_fish = False
