import os
import threading
import webbrowser
import argparse
import pyperclip
from tkinter import Tk, messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
from flask import Flask, send_file, jsonify
from pathlib import Path


def isFile(path):
    return os.path.isfile(path)

def isDir(path):
    return os.path.isdir(path)

class FileServer(threading.Thread):
    def __init__(self, port, share_path):
        super().__init__()
        self.app = Flask(__name__)
        self.shared_path = share_path
        self.port = port
        self.daemon = True

        # 处理文件内容请求或列出文件夹内容
        @self.app.route('/', methods=['GET'])
        def get_file_or_list_files():
            if isDir(self.shared_path):
                files = [f.name for f in Path(self.shared_path).iterdir()]
                return jsonify({'files': files})
            else:
                return jsonify({'files': [os.path.basename(self.shared_path)]})

        # 处理文件内容请求或列出文件夹内容
        @self.app.route('/<path:filename>', methods=['GET'])
        def get_file_or_list_files_by_path(filename):
            full_path = os.path.join(self.shared_path, filename)

            # 如果共享路径为文件时
            if isFile(self.shared_path) and os.path.basename(self.shared_path) == filename:
                return send_file(self.shared_path, as_attachment=True)
            # 如果共享路径为文件夹时
            elif isDir(self.shared_path) and os.path.exists(full_path):
                if isFile(full_path):
                    return send_file(full_path, as_attachment=True)
                else:
                    files = [f.name for f in Path(full_path).iterdir()]
                    return jsonify({'files': files})

            return "File or directory not found", 404

    def run(self):
        self.app.run(port=self.port)

class FileShareApp:
    def __init__(self, root, file_share_server):
        self.root = root
        self.root.title("File Share Tool")

        self.file_share_server = file_share_server

        self.label = ttk.Label(self.root, text=f"Shared Path: {file_share_server.shared_path}")
        self.label.pack()

        self.url = f"http://localhost:{self.file_share_server.port}"

        if isFile(file_share_server.shared_path): 
            self.url += "/" + os.path.basename(file_share_server.shared_path)
        
        self.copy_button = ttk.Button(self.root, text="Copy Link", command=self.copy_link)
        self.copy_button.pack(side="left", padx=5, anchor="center")

        self.open_button = ttk.Button(self.root, text="Open in Browser", command=self.open_in_browser)
        self.open_button.pack(side="left", padx=5, anchor="center")

        self.file_share_server.start()

    def copy_link(self):
        link = self.url
        pyperclip.copy(link)
        messagebox.showinfo("Link Copied", f"The link '{link}' has been copied to the clipboard.")

    def open_in_browser(self):
        link = self.url
        webbrowser.open(link)

def main():
    parser = argparse.ArgumentParser(description="File Share Tool")
    parser.add_argument("--port", type=int, default=8000, help="Port number for the server")
    parser.add_argument("--shared-path", help="Path of the file or folder to share")
    args = parser.parse_args()

    if args.shared_path:
        root = ThemedTk(theme="arc")
        app = FileShareApp(root, FileServer(args.port, args.shared_path))
        root.mainloop()
    else:
        messagebox.showinfo("Command Line Run Required", "Please run the program with command-line arguments.")

if __name__ == "__main__":
    main()
