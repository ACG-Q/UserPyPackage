import subprocess
import sys

def main():
    """
    Compiles the Python script into a standalone executable using Nuitka.
    """

    # Determine the system type
    system_type = sys.platform

    # Set the Nuitka command-line arguments
    nuitka_args = [
        "python",
        "-m",
        "nuitka",
        "--lto=yes", # 启用链接时间优化
        "--standalone", # 独立环境
        "--show-progress", # 显示编译的进度，很直观
        "--show-memory", # 显示内存占用，很直观
        "--output-dir=dist", # 输出目录
        "--plugin-enable=tk-inter", # 使tkinter可用
        "--include-data-file=./icon.png=./icon.png", # 包含图标
        "--include-data-file=./favicon.ico=./favicon.ico", # 包含图标
        "--onefile", # 单个exe文件
        "--remove-output", # 清理打包过程中生成的临时文件
    ]

    # Add platform-specific arguments
    if system_type == "darwin":
        sys.exit("MacOS is not supported yet.")
    elif system_type == "linux":
        nuitka_args.append("--enable-plugin=upx") # 使upx可用
        nuitka_args.append("--upx-binary=./upx/upx")
        nuitka_args.append("--linux-onefile-icon=./icon.png")
    else:
        nuitka_args.append("--enable-plugin=upx") # 使upx可用
        nuitka_args.append("--upx-binary=./upx/upx.exe")
        nuitka_args.append("--windows-icon-from-ico=./favicon.ico")
        nuitka_args.append("--windows-product-name=\"File Centipede Automatic Activation\"")
        nuitka_args.append("--windows-product-version=1.0.0")

    # Add the input script as the last argument
    nuitka_args.append("main.py")

    # Run Nuitka
    # subprocess.check_call(nuitka_args)
    # 创建子进程并执行命令
    process = subprocess.Popen(nuitka_args, stdin=subprocess.PIPE, shell=True)
    # 向子进程发送输入 "Yes"
    process.communicate(input=b"Yes\n")

if __name__ == "__main__":
    main()
