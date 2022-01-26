# Torchlight1-achievementbot
 This is a silly program that uses OpenCV's image recognition and tries to help the user achieve achievements. 

Program has two modes: 

1. A fishing mode that tries to go fish & then run the fishing minigame.For the achievement "Fisher King".
2. A clickermode that uses a glitch in a mod to make a lot of purchases of an item that costs -1 and then sell it. For achievements that need gold (~10+) as well as "Cash for Trash".
3. A mode that resets a character who has died. Due to it being very simple to set up a character + enemies by a staircase there's no other function than to click the "ressurect at stairs" button (and a tracker that sets a goal of amount of deaths). For the "Tormented" achievement.


NOTE: This program will use your mouse as you run it. pyautogui (which is the module that does it) has a failsafe: drag the mouse to a corner of the screen to have it trigger. Otherwhise: if you ever press space while the program is running it will trigger the program to exit as soon as possible.

Idea came from https://github.com/ClarityCoders/ComputerVision-OpenCV/tree/master/Lesson3-TemplateMatching 

- Uses OpenCV for image recognition - https://opencv.org/
- Uses pyautogui to click the screen - https://pyautogui.readthedocs.io/en/latest/
- Uses mss for screen capture - https://python-mss.readthedocs.io/usage.html
- And to process that screen capture for OpenCV: using NumPy - https://numpy.org/
- Uses "keyboard" to use the keyboard - https://github.com/boppreh/keyboard
- Uses tesseract to interpret the amount of cash made in the 2nd mode in attempt to finetune performance - https://github.com/tesseract-ocr/tesseract
