#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      anrik
#
# Created:     12-01-2022
# Copyright:   (c) anrik 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from FisherHelper import FishHelper
import cv2
import logging
from pyautogui import click
from time import time, sleep

class WantonNihilist(FishHelper):
    _needle_killscreen = cv2.imread("needle_killed.png")
    _needle_hud = cv2.imread("needle_hud.png")
    _start_time = None
    _times_died = None

    def __init__(self,game_dimensions):
        self._game_dimensions = game_dimensions
        FishHelper.__init__(self)

    def go_die(self, wanted_deaths = None):
        self._times_died = 0
        self._start_time = round(time())
        time_since_last_death = self._start_time
        state = 0
        time_for_stats = False

        if wanted_deaths is None:
            wanted_deaths = 500

        while self._times_died < wanted_deaths and time() - time_since_last_death < 120 and self._time_to_fish:
            sleep(0.2)
            if state == 0:
                fresh_screen = self.grab_screen(True, dimensions=self._game_dimensions)
                state = self.state_decide(fresh_screen,0.85, one = self._needle_killscreen, two = self._needle_killscreen)

            if state == 1:
                time_since_last_death = round(time())
                self._times_died += 1
                if self._times_died % 20 == 0 and self._times_died != 0:
                    time_for_stats = True
                curr_res = self.get_matchtemplate_results(fresh_screen, self._needle_killscreen)
                max_loc = curr_res["max_loc"]
                click_x = max_loc[0] + 93 + self._game_dimensions["left"]
                click_y = max_loc[1] + 17 + self._game_dimensions["top"]

                click(click_x,click_y)

                state = 0

            if state == 2:
                ## I thought I needed to set up a more complicated "look for deaths" method
                ## but apparently its easy to set up a quick death at stairs.
                state = 0
                print("lol yo")
                pass

            if time_for_stats:
                self.__print_stats(wanted_deaths)
                time_for_stats = False

        self.__print_stats(wanted_deaths)

        self.log_end()

    def __print_stats(self, wanted_deaths):
        time_running = round(time()) - self._start_time
        print(f"I've now died {self._times_died} times and it took {time_running} seconds.")
        print("That's {} deaths per minute!".format(round(self._times_died/(time_running/60),2)))

        time_left = round((time_running / self._times_died) * (wanted_deaths - self._times_died))

        if self._times_died < wanted_deaths:
            time_left_min = round(time_left / 60)
            print(f"With this pace, I'm done in {time_left} seconds (about {time_left_min} minutes)")
        else:
            minutes = round((time_running - time_running % 60) / 60)
            seconds = time_running % 60
            print(f"Achieved {wanted_deaths} deaths! Ending program.")
            print(f"Total runtime was {minutes} minutes and {seconds} seconds.")
