import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import threading
import os
import time
import pystray
from pyautostart import SmartAutostart
from PIL import Image

from activation_codes import get_activation_codes, input_activation_code

program_name = "文件蜈蚣自动激活器"  # 替换为你的程序名称
executable_path = os.path.abspath(__file__)  # 替换为你的可执行文件路径


class ActivationCodeApp:
    def __init__(self, root):
        self.root = root



        self.root.title("激活")
        self.root.iconbitmap('favicon.ico')
        

        width = 200
        height = 135
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int(screen_width / 2 - width / 2)
        y = int(screen_height / 2 - height / 2)
        size = '{}x{}+{}+{}'.format(width, height, x, y)
        self.root.geometry(size)

        self.root.minsize(width, height)

        self.autostart = SmartAutostart()

        # 初始化布尔变量，用于开机自启选项的状态
        self.start_on_startup_var = tk.BooleanVar()
        self.start_on_startup_var.set(self.is_startup_enabled())  # 设置为开机自启的状态

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
            self.set_startup_program()
        else:
            # 如果取消选中开机自启，禁用开机自启动
            self.disable_startup_program()

    def create_run(self):
        while True:
            activation_codes = get_activation_codes()
            if activation_codes:
                print(activation_codes)
                isOk = input_activation_code("文件蜈蚣 - 激活码", activation_codes)
                if isOk:
                    break
                time.sleep(2)
            else:
                time.sleep(60)
        messagebox.showinfo("提示", "激活码已输入，点击确定后3秒后自动关闭")
        time.sleep(3)
        self.exit_app()

    def show_tray_icon(self):
        image = Image.open("icon.png")  # Replace with the path to your icon image
        menu = (
            pystray.MenuItem("显示主页面", self.show_main_window),
            pystray.MenuItem("退出", self.exit_app)
        )
        self.tray_icon = pystray.Icon("name", image, "激活码自动输入器", menu)
        self.tray_icon.run()


    def is_startup_enabled(self):
        return self.autostart.is_enabled(name=program_name)

    def set_startup_program(self):
        options = {
            "args": [
                executable_path
            ]
        }
        self.autostart.enable(name=program_name, options=options)

    def disable_startup_program(self):
        self.autostart.disable(name=program_name)

    def exit_app(self):
        self.root.quit()
        self.root.destroy()
        self.tray_icon.stop()  # Stop the tray icon before exiting

    def show_main_window(self):
        self.root.deiconify()



def main():
    root = tk.Tk()
    # 隐藏窗口
    root.withdraw()
    app = ActivationCodeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()