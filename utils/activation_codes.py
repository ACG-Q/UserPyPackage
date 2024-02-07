import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# 代码更新重试次数
get_code_retry_times = 3
code_list_file_name = "code_list.json"


def merge_list(list1, list2):
    # 判断list1是不是数组
    if not isinstance(list1, list):
        list1 = []

    if not isinstance(list2, list):
        list2 = []

    for item2 in list2:
        start2 = item2["start"]
        end2 = item2["end"]
        found = False

        for item1 in list1:
            start1 = item1["start"]
            end1 = item1["end"]

            if start1 == start2 and end1 == end2:
                item1["code"] = item2["code"]
                found = True
                break

        if not found:
            list1.append(item2)
    
    return list1

def get_code_list_from_remote():
    result = []

    url = "https://filecxx.com/zh_CN/activation_code.html"
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")
    codes_element = soup.find(id="codes")
    codes_text = codes_element.get_text(strip=True)

    codes_list = codes_text.split("\n\n")
    

    for i in range(len(codes_list)):
        codes = codes_list[i].split("\n")
        start_end = codes[0]
        code = codes[1]

        start, end = start_end.split(" - ")

        data = {
            "start": start,
            "end": end,
            "code": code
        }
        result.append(data)

    return result

def update_code_list_by_local_force(dir):
    global get_code_retry_times
    try:
        result = get_code_list_from_remote()
        path = os.path.join(dir, code_list_file_name)

        with open(path, "w") as f:
            json.dump(result, f, indent=4)
        print("激活码列表已强制更新")
    except KeyboardInterrupt:
        print("Ctrl+C detected. Exiting...")
        return
    except BaseException as e:
        print("强制更新激活码列表失败，正在重试", e)
        if get_code_retry_times > 0:
            get_code_retry_times -= 1
            update_code_list_by_local_force(dir)
        else:
            print("强制更新激活码列表失败")
            get_code_retry_times = 3

def update_code_list_by_local(dir):
    global get_code_retry_times
    try:
        result = get_code_list_from_remote()
        path = os.path.join(dir, code_list_file_name)

        if os.path.exists(path):
            with open(path, "r") as f:
                old_result = json.load(f)
            result = merge_list(old_result, result)

        with open(path, "w") as f:
            json.dump(result, f, indent=4)
        print("激活码列表已更新")
    except KeyboardInterrupt:
        print("Ctrl+C detected. Exiting...")
        return
    except BaseException as e:
        print("更新激活码列表失败，正在重试", e)
        if get_code_retry_times > 0:
            get_code_retry_times -= 1
            update_code_list_by_local(dir)
        else:
            print("更新激活码列表失败")
            get_code_retry_times = 3
def get_code_in_code_list(dir):
    path = os.path.join(dir, code_list_file_name)
    if os.path.exists(path):
        with open(path, "r") as f:
            code_list = json.load(f)

        now_time = int(datetime.now().timestamp())
        found = False

        for i in range(len(code_list)):
            start_unix = int(datetime.strptime(code_list[i]["start"], "%Y-%m-%d %H:%M:%S").timestamp())
            end_unix = int(datetime.strptime(code_list[i]["end"], "%Y-%m-%d %H:%M:%S").timestamp())
            if start_unix <= now_time <= end_unix:
                found = True
                return code_list[i]["code"]
                break

        if not found:
            return None
    else:
        return None


if __name__ == "__main__":
    update_code_list_by_local_force(".")
    print(get_code_in_code_list("."))
