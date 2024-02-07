import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import threading
import os
import time
import sys
import pystray
import argparse
from pyautostart import SmartAutostart
from PIL import Image

from utils import update_code_list_by_local, update_code_list_by_local_force, get_code_in_code_list, input_activation_code

program_name = "文件蜈蚣自动激活器"  # 替换为你的程序名称
version = "1.0.0"

if getattr(sys, 'frozen', False):
    # 脚本已被打包
    executable_path = sys.executable
    # sys._MEIPASS 就是这些依赖文件所在文件夹的路径
    dependent_dir = sys._MEIPASS
else:
    # 脚本未被打包
    executable_path = os.path.abspath(sys.argv[0])  # 替换为你的可执行文件路径
    dependent_dir = os.path.dirname(os.path.abspath(executable_path))

executable_dir = os.path.dirname(os.path.abspath(executable_path))

window_icon = os.path.join(dependent_dir, "favicon.ico")
tray_icon = os.path.join(dependent_dir, "icon.png")

autostart = SmartAutostart()

def close_message_box(message_box, callback):
    message_box.destroy()
    if callback: callback()

def show_auto_close_message(title, message, duration, callback):
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    message_box = tk.Toplevel(root)
    message_box.title(title)
    message_label = tk.Label(message_box, text=message)
    message_label.pack(padx=20, pady=20)

    root.after(duration, lambda: close_message_box(message_box, callback))
    root.mainloop()

class UpdateCode(threading.Thread):
    def run(self):
        update_code_list_by_local(executable_dir)
def is_startup_enabled():
    return autostart.is_enabled(name=program_name)
def set_startup_program():
    options = {
        "args": [
            f"\"{executable_path}\""
        ]
    }
    autostart.enable(name=program_name, options=options)
def disable_startup_program():
    autostart.disable(name=program_name)

class ActivationCodeApp:
    def __init__(self, root):
        self.root = root

        self.root.title("激活")
        self.root.iconbitmap(window_icon)

        width = 200
        height = 135
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int(screen_width / 2 - width / 2)
        y = int(screen_height / 2 - height / 2)
        size = '{}x{}+{}+{}'.format(width, height, x, y)
        self.root.geometry(size)

        self.root.minsize(width, height)

        # 初始化布尔变量，用于开机自启选项的状态
        self.start_on_startup_var = tk.BooleanVar()
        self.start_on_startup_var.set(is_startup_enabled())  # 设置为开机自启的状态

        self.create_gui()

    def create_gui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(main_frame, text="激活码自动输入器", font=("微软雅黑", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        startup_checkbox = ttk.Checkbutton(main_frame, text="开机自启", variable=self.start_on_startup_var, command=self.toggle_startup)
        startup_checkbox.grid(row=1, column=0, columnspan=2, pady=5)

        tray_process = threading.Thread(target=self.show_tray_icon, daemon=True)
        tray_process.start()

        activation_codes = threading.Thread(target=self.create_run, daemon=True)
        activation_codes.start()

    def toggle_startup(self):
        # 开机自启选项状态改变时触发
        if self.start_on_startup_var.get():
            # 如果选中了开机自启，启用开机自启动
            set_startup_program()
        else:
            # 如果取消选中开机自启，禁用开机自启动
            disable_startup_program()

    def create_run(self):
        while True:
            activation_codes = get_code_in_code_list(executable_dir)
            print("获取激活码", activation_codes)
            if activation_codes:
                isOk = input_activation_code("文件蜈蚣 - 激活码", activation_codes)
                if isOk:
                    break
                time.sleep(2)
            else:
                print("未获取到激活码, 更新激活码列表")
                UpdateCode().start()
                time.sleep(60)
        show_auto_close_message("提示", "激活码已输入，点击确定后3秒后自动关闭", 3000, self.exit_app)

    def show_tray_icon(self):
        image = Image.open(tray_icon)  # Replace with the path to your icon image
        menu = (
            pystray.MenuItem("显示主页面", self.show_main_window),
            pystray.MenuItem("退出", self.exit_app)
        )
        self.tray_icon = pystray.Icon("name", image, "激活码自动输入器", menu)
        self.tray_icon.run()


    def exit_app(self):
        self.root.quit()
        self.root.destroy()
        self.tray_icon.stop()  # Stop the tray icon before exiting

    def show_main_window(self):
        self.root.deiconify()

# 命令行参数解析
def parse_args():
    parser = argparse.ArgumentParser(description="文件蜈蚣自动激活器", epilog="直接运行程序以显示用户界面")

    command_group = parser.add_argument_group("命令行参数")
    command_group.add_argument("-s", "--startup", action="store_true", help="开机自启")
    command_group.add_argument("-c", "--code", action="store_true", help="获取激活码")
    command_group.add_argument("-v", "--version", action="store_true", help="版本号")

    update_group = parser.add_argument_group("更新参数")
    update_group.add_argument("-u", "--update", action="store_true", help="更新激活码列表")
    update_group.add_argument("-f", "--force", action="store_true", help="强制更新激活码列表")

    args = parser.parse_args()

    if args.force and not args.update:
        parser.error("'-f' 选项只能与 '-u' 选项一起使用")
        sys.exit(0)

    if args.update:
        if args.force:
            # 强制更新激活码列表
            update_code_list_by_local_force(executable_dir)
        else:
            # 更新激活码列表
            update_code_list_by_local(executable_dir)
        sys.exit(0)

    if args.startup:
        if is_startup_enabled():
            disable_startup_program()
            print("开机自启已禁用")
        else:
            set_startup_program()
            print("开机自启已启用")
        sys.exit(0)

    if args.code:
        activation_codes = get_code_in_code_list(executable_dir)
        print(f"激活码: {activation_codes}")
        sys.exit(0)

    if args.version:
        print("版本号", version)
        sys.exit(0)

def main():
    parse_args()
    UpdateCode().start()
    root = tk.Tk()
    # 隐藏窗口
    root.withdraw()
    # 关闭按钮改为回到托盘（隐藏窗口）
    root.protocol("WM_DELETE_WINDOW", lambda: root.withdraw())
    app = ActivationCodeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()