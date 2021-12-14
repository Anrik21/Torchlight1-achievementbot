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

import cv2
import sys
import pyautogui
import random
import keyboard
import numpy
from pathlib import Path
from glob import glob
from mss import mss
from time import time, sleep

time_to_fish = True

def main(monitor = None):
    # setup variables here lol
    needle_hole = cv2.imread("needle_holetime.png")
    needle_fishbutton = cv2.imread("needle_fishbutton1.png")
    needle_nothing = cv2.imread("needle_nothing.png")
    needle_oktime = cv2.imread("needle_oktime.png")

    #Setup folders for original needles
    fail_folder = Path.cwd()
    win_folder = f"{fail_folder}/Pictures of wins/"
    fail_folder = f"{fail_folder}/Pictures of fails/"

    #Maybe put in function due to we will be adding and updating the files in these folders
    needle_folder_wins = glob(win_folder+"*.png")
    needle_folder_fails = glob(fail_folder+"*.png")

    win_needles = []
    fail_needles = []
    ''' Commenting this out: lets reset our stats every time to ensure no mess
    if len(needle_folder_wins) > 0:
        for needle in needle_folder_wins:
            loaded_needle = cv2.imread(needle)
            win_needles.append(loaded_needle)
    if len(needle_folder_fails) > 0:
        for needle in needle_folder_fails:
            loaded_needle = cv2.imread(needle)
            fail_needles.append(loaded_needle)
    '''
    global time_to_fish #is this a good way to exit?
    keyboard.add_hotkey('space',on_space)

    print("For 15 seconds, program is now searching for Torchlight window")

    game_dimensions = setup_game_screen(monitor)
    inside_dimensions = None

    if game_dimensions is None:
        sys.exit("Program was not able to find Torchlight within 15 seconds. Exiting")

    #initial hole finding here
    print("Torchlight window was found. Now an initial finding of the fishing hole will be done")

    deadline = time()
    while inside_dimensions is None:
        inside_dimensions = find_initial_fishing_hole(game_dimensions,needle_hole,needle_fishbutton)
        result = get_matchtemplate_results(grab_screen(True,dimensions = game_dimensions),needle_fishbutton)
        temp = result["max_loc"]
        x_offset = temp[0] + game_dimensions["left"] -115
        y_offset = temp[1] + game_dimensions["top"] -115
        if time() - deadline > 15:
            sys.exit("Program did not find the initial fishing hole within 15 seconds. Exiting.")

    time_to_fish = True
    deadline = time()
    state = state_decide(needle_hole,needle_oktime,needle_fishbutton,grab_screen(True,dimensions=game_dimensions),0.9)
    fish_wins = 0
    fish_fails = len(fail_needles)
    min_wait = 5
    max_wait = 15
    stat_dict = {
    "total_fish_caught" : 0,
    "time_in_lottery": 0,
    "lottery_attempts": 0,
    "attempts": 0,
    "recent_fish": 0,
    "recent_fails" :0,
    "highest_perf" : 0
    }
    time_for_stats = False
    fish_deadline = 0
    threshold_nudge = 0.005
    win_stats = []

    print(f"Game was found, hole was found and clicked.")

    print(f"All setup is done. Fishing loop is starting with state {state}.")

    while time_to_fish: #or time() - deadline < 120:
        sleep(0.15) #naive attempt to limit amount of calculation with ~60fps
        # states are 1 (fish), 2 (ok) , 3 (hole), 0 for state find
        if state == 0:
            state = state_decide(needle_hole,needle_oktime,needle_fishbutton,grab_screen(True, dimensions=game_dimensions),0.86)
            if time_for_stats:
                stat_dict = print_some_stats(stat_dict)
                time_for_stats = False
                if stat_dict["total_fish_caught"] > 105:
                    time_to_fish = False
        #fishing logic
        if state == 1: # this could live in its own function, but needs many globals :(
            have_not_clicked = True
            time_to_click = False
            while have_not_clicked and time_to_fish:
                if len(win_needles) < 1:
                    click_time = random.randint(min_wait,max_wait) #these constants need to be checked
                    print(f"Fishing lottery started. Waiting for {click_time} seconds")
                    sleep(click_time)
                    time_to_click = True
                    #when its time to click, check if there's a high chance of a failpic
                    click_screen = grab_screen(False,inside_dimensions)
                    clean_screen = click_screen[:,:,:3]
                    result = get_matchtemplate_results(clean_screen,needle_fishbutton) # ISSUE! The max_loc returns the max loc of the "inner dimension"
                    if len(fail_needles) > 1:
                        if stat_dict["lottery_attempts"] > 5:
                            threshold_nudge += threshold_nudge
                        for needle in fail_needles:
                            if find_item_on_screen(needle,0.945+threshold_nudge,screen_grab=clean_screen):
                                time_to_click = False
                                break
                    if time_to_click:
                        center = get_center(result["max_loc"], needle_fishbutton)
                        pyautogui.click(center[0] + x_offset, center[1] + y_offset)
                        sleep(1.5)
                        stat_dict["lottery_attempts"] += 1
                        stat_dict["attempts"] +=1
                        if stat_dict["attempts"] % 10 == 0:
                            time_for_stats = True
                        #now send the click_screen to the OK function
                        have_not_clicked = False
                        threshold_nudge = 0.005
                        if len(fail_needles) > 1:
                            min_wait = 2
                            max_wait = 7
                        else:
                            min_wait = 5
                            max_wait = 15
                    else:
                        min_wait = 0
                        max_wait = 3
                else:
                    if stat_dict["time_in_lottery"] == 0:
                        stat_dict["time_in_lottery"] = time() - deadline
                        fish_deadline = time()
                        threshold_nudge = 0.005
                    click_screen = grab_screen(False,inside_dimensions)
                    clean_screen = click_screen[:,:,:3]
                    result = get_matchtemplate_results(clean_screen,needle_fishbutton)
                    if time() - fish_deadline > 30:
                        threshold_nudge += threshold_nudge

                    stat_track = 0
                    for needle in win_needles:
                        if find_item_on_screen(needle,0.985-threshold_nudge,screen_grab=clean_screen):
                            time_to_click = True
                            break
                        stat_track +=1

                    for needle in fail_needles:
                        if find_item_on_screen(needle,0.96,screen_grab=clean_screen):
                            time_to_click = False
                            stat_track = None
                            break

                    if time_to_click:
                        center = get_center(result["max_loc"], needle_fishbutton)
                        pyautogui.click(center[0] + x_offset, center[1] + y_offset)
                        sleep(1.5)
                        fish_deadline = time()
                        threshold_nudge = 0.005
                        stat_dict["attempts"] +=1
                        if stat_dict["attempts"] % 10 == 0:
                            time_for_stats = True
                        #now send the click_screen to the OK function
                        have_not_clicked = False
            state = 0

        if state == 2:
            if find_item_on_screen(needle_nothing,0.95, dimensions=game_dimensions):
                #it was a fail, save the image
                if fish_fails < 20: #fully arbitrary number
                    saved_image = save_picture(fish_fails, click_screen, folder=fail_folder)
                    fail_needles.append(cv2.imread(saved_image))
                    fish_fails += 1
##              else:
##                    fail_needles.pop(0)
##                    fish_fails = 0
                stat_dict["recent_fails"] += 1
            else:
                #it was a win, save the image as win
                if fish_wins < 5 : #fully arbitrary number
                    saved_image = save_picture(fish_wins, click_screen, folder=win_folder)
                    if fish_wins < 1:
                        win_needles.append(cv2.imread(saved_image))
                        fish_wins += 1
##                    elif threshold_nudge > 4 * threshold_nudge:
##                        win_needles.append(cv2.imread(saved_image))
##                        fish_wins += 1
                stat_dict["recent_fish"] += 1
                stat_dict["total_fish_caught"] +=1
            if find_and_click(game_dimensions,needle_oktime,0.9):
                sleep(1.5)
                state = 0

        if state == 3:
            if find_and_click(game_dimensions,needle_hole, 0.9):
                sleep(1.5)
                state = 0

    print("Program is exiting. Here are the final stats.")
    stat_dict = print_some_stats(stat_dict, round(time() - deadline))

def print_some_stats(stat_dict, final = None):
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


def on_space():
    global time_to_fish
    time_to_fish = False

def state_decide(hole_needle, ok_needle, fish_needle, clean_screen_img, threshold):
    hole_result = get_matchtemplate_results(clean_screen_img, hole_needle)
    fish_result = get_matchtemplate_results(clean_screen_img, fish_needle)
    ok_result = get_matchtemplate_results(clean_screen_img, ok_needle)

    #save_picture(1337,clean_screen_img)

    hole = hole_result["max_val"]
    fish = fish_result["max_val"]
    ok = ok_result["max_val"]

    if ok > threshold or hole > threshold or fish > threshold:
        if fish > hole and fish > ok:
            return 1
        elif ok > fish and ok > hole:
            return 2
        else:
            return 3
    else:
        return 0

def find_initial_fishing_hole(dimensions, hole_needle, fish_needle):
    find_and_click(dimensions, hole_needle, 0.9)
    sleep(1.5)
    #Doing a manual check to be set up "screen in screen" for smaller comparisons
    match_result = get_matchtemplate_results(grab_screen(True,dimensions),fish_needle)
    if match_result["max_val"] > .85:
        inside_dimensions = dimensions.copy()
        point_one = match_result["max_loc"]
        point_two = fish_needle.shape

        # 115 may look random but it's approx the size of the max sized fishcircle in the minigame at this resolution
        inside_dimensions = change_dimensions(inside_dimensions, (point_one[0]-115,point_one[1] -115), (point_two[0]+230,point_two[1]+230))
    else:
        inside_dimensions = None

    return inside_dimensions

def find_item_on_screen(needle, threshold, dimensions = None, screen_grab = None):
    if screen_grab is None and dimensions is not None:
        screen_grab = grab_screen(True,dimensions)
    if screen_grab is None and dimensions is None:
        return false
    search = get_matchtemplate_results(screen_grab, needle)

    if search["max_val"] > threshold:
        return True
    return False

def find_and_click(game_dimensions, needle, threshold):
    clean_source = grab_screen(True, game_dimensions)
    hole_search = get_matchtemplate_results(clean_source, needle)
    if hole_search["max_val"] > threshold:
        loc = get_center(hole_search["max_loc"], needle)
        pyautogui.click(x = loc[0] +game_dimensions["left"],y=loc[1]+game_dimensions["top"])
        return True
    return False

def setup_game_screen(monitor):
    program_needle = cv2.imread("needle_torchprogram.png")
    find_game_timer = time()
    torch_found = False
    game_window = None
    if monitor is None:
        monitor = 1

    while time() - find_game_timer < 15 and not torch_found:
        scr_source = grab_screen(True,monitor=monitor)
        result_dict = get_matchtemplate_results(scr_source, program_needle)

        max_val = result_dict["max_val"]
        max_loc = result_dict["max_loc"]
        print(f"Max val is {max_val}")
        if max_val > .90:
            print(f"Max val was higher than 90%, so I think I found it at...")
            print(f"Max val: {max_val} Max loc: {max_loc}")
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
            print("Did not find it yet...")
        sleep(0.5)

    return game_window

def get_center(max_loc, needle):
    center = (max_loc[0] + round(needle.shape[1]/2), max_loc[1] + round(needle.shape[0]/2))

    return center

def setup_needles(list_of_picturefiles):

    collection_of_needles = []

    for picturefiles in list_of_picturefiles:
        picturefiles = cv2.imread(picturefiles)
        collection_of_needles.append(picturefiles)

    return collection_of_needles

def grab_screen(clean, dimensions = None, monitor = None ):

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


def change_dimensions(dimensions, point_one, point_two):
    '''
    Changes dimensions (a dict with 4 valuepairs: left, top, width & height)
    to the given points: top left will be point one, bottom right point two.
    '''
    dimensions["left"] += point_one[0]
    dimensions["top"] += point_one[1]
    dimensions["width"] = point_two[0]
    dimensions["height"] = point_two[1]

    return dimensions

def get_matchtemplate_results(cleaned_source, needle):
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

def save_picture(pic_ID, picture, folder = None, point_one = None, point_two = None):
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



if __name__ == '__main__':
    main()
