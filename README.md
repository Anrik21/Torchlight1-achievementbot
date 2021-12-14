# Torchlight1-achievementbot
 This is a silly program that uses OpenCV's image recognition and tries to help the user achieve achievements. Currently only fishing implemented.

NOTE: This program will use your mouse as you run it. pyautogui (which is the module that does it) has a failsafe: drag the mouse to a corner of the screen to have it trigger. Otherwhise: if you ever press space while the program is running it will trigger the program to exit as soon as possible.

Idea came from https://github.com/ClarityCoders/ComputerVision-OpenCV/tree/master/Lesson3-TemplateMatching 

- Uses OpenCV for image recognition - https://opencv.org/
- Uses pyautogui to click the screen - https://pyautogui.readthedocs.io/en/latest/
- Uses mss for screen capture - https://python-mss.readthedocs.io/usage.html
- And to process that screen capture for OpenCV: using NumPy - https://numpy.org/
- Uses "keyboard" to use the keyboard - https://github.com/boppreh/keyboard
