import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# 代码更新重试次数
get_code_retry_times = 3
code_list_file_name = "code_list.json"


# 列表合并
# list1
# [{
#     "start": 123123,
#     "end": 123123,
#     "code": ""
# }]
# list2
# [{
#     "start": 123123,
#     "end": 123123,
#     "code": ""
# }]
def merge_list(list1, list2):
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



def update_code_list_by_local(dir:str):
    global get_code_retry_times
    try:
        path = os.path.join(dir, code_list_file_name)
        # 发送GET请求并获取网页内容
        url = "https://filecxx.com/zh_CN/activation_code.html"
        response = requests.get(url)
        html_content = response.text

        # 使用BeautifulSoup解析网页内容
        soup = BeautifulSoup(html_content, "html.parser")

        # 获取id为codes的内容
        codes_element = soup.find(id="codes")
        codes_text = codes_element.get_text(strip=True)

        # 解析codes内容并保存为JSON
        codes_list = codes_text.split("\n\n")
        result = []

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

        if os.path.exists(path):
            with open(path, "r") as f:
                old_result = json.load(f)
            result = merge_list(old_result, result)

        # 保存为JSON文件
        with open(path, "w") as f:
            json.dump(result, f, indent=4)
    except KeyboardInterrupt:
        print("Ctrl+C detected. Exiting...")
        return
    except BaseException as e:
        print("更新激活码列表失败, 正在重试", e)
        if get_code_retry_times > 0:
            get_code_retry_times = get_code_retry_times - 1
            update_code_list_by_local(dir)
        else:
            print("更新激活码列表失败")

def get_code_in_code_list(dir:str):
    path = os.path.join(dir, code_list_file_name)
    if os.path.exists(path):
        # 获取JSON文件内容
        with open(path, "r") as f:
            code_list = json.load(f)

        # 获取当前时间
        now_time = int(datetime.now().timestamp())

        # 获取当前时间在时间列表中的索引
        for i in range(len(code_list)):
            start_unix = int(datetime.strptime(code_list[i]["start"], "%Y-%m-%d %H:%M:%S").timestamp())
            end_unix = int(datetime.strptime(code_list[i]["end"], "%Y-%m-%d %H:%M:%S").timestamp())
            if start_unix <= now_time <= end_unix:
                return code_list[i]["code"]
                break
    
    return None



if __name__ == "__main__":
    update_code_list_by_local(".")
    print(get_code_in_code_list("."))