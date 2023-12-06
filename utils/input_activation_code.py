import os
from pyautogui import moveTo, click, hotkey, press
from pygetwindow import getWindowsWithTitle
from pyperclip import copy
from time import sleep


def input_activation_code(window_title, activation_code):
    try:
        target_window = getWindowsWithTitle(window_title)[0]
        target_window.restore()
        target_window.activate()
        sleep(0.15)

        input_box_x = (target_window.left + target_window.right) // 2
        input_box_y = (target_window.top + target_window.bottom) // 2 - 15
        moveTo(input_box_x, input_box_y)
        click()

        hotkey('ctrl', 'a')
        press('delete')

        copy(activation_code)
        hotkey('ctrl', 'v')

        sleep(0.15)

        confirm_button_x = target_window.right - 60
        confirm_button_y = target_window.bottom - 30
        moveTo(confirm_button_x, confirm_button_y)
        click()

        sleep(0.15)

        hotkey('enter')
        return True
    except KeyboardInterrupt:
        print("Ctrl+C detected. Exiting...")
        return
    except IndexError:
        print(f"未找到标题为 '{window_title}' 的窗口。")
        return False
    except Exception as e:
        print("发生错误:", e)
        return False