import datetime
import os
from json import load, dump
from pyautogui import moveTo, click, hotkey, press
from pygetwindow import getWindowsWithTitle
from pyperclip import copy
from re import compile
from requests import get
from time import sleep

def get_local_activation_code(activation_codes_path):
    try:
        with open(activation_codes_path, 'r') as f:
            codes = load(f)
            today = datetime.date.today().strftime('%Y-%m-%d')
            for code in codes:
                if code["Validity Period"].startswith(today):
                    return code["ActivationCode"]
    except Exception as e:
        print("读取本地激活码出错:", e)
        return None

def fetch_online_activation_codes(url):
    try:
        response = get(url)
        html_content = response.text

        pattern = compile(r'(\d{4}-\d{2}-\d{2} 00:00:00 - \d{4}-\d{2}-\d{2} 00:00:00).*?\n(.+?)\n')

        results = pattern.findall(html_content)

        if results:
            today_date = datetime.date.today()
            codes = []
            for result in results:
                date = result[0]
                code = result[1]
                code_date = datetime.datetime.strptime(date[:10], '%Y-%m-%d').date()
                if code_date >= today_date:
                    codes.append({"Validity Period": date, "ActivationCode": code})
            return codes
        else:
            print("没有找到符合条件的激活码")
            return []

    except Exception as e:
        print("获取在线激活码出错:", e)
        return []

def save_activation_codes(activation_codes, activation_codes_path):
    try:
        activation_codes_dir = os.path.dirname(activation_codes_path)
        if not os.path.exists(activation_codes_dir):
            os.makedirs(activation_codes_dir)
        with open(activation_codes_path, 'w') as f:
            dump(activation_codes, f, indent=2)
    except Exception as e:
        print("保存激活码出错:", e)

def get_activation_codes():
    activation_codes_path = os.path.join(os.environ['APPDATA'], 'File Centipede', 'ActivationCodes.json')
    local_codes = get_local_activation_code(activation_codes_path)

    if local_codes:
        return local_codes

    online_codes = fetch_online_activation_codes('https://filecxx.com/zh_CN/activation_code.html')
    if online_codes:
        save_activation_codes(online_codes, activation_codes_path)
        return online_codes

    return None

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
    except IndexError:
        print(f"未找到标题为 '{window_title}' 的窗口。")
        return False
    except Exception as e:
        print("发生错误:", e)
        return False