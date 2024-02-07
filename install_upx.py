import os
import shutil
import subprocess
import sys
import urllib.request
import json

def get_latest_upx_version():
    """
    Gets the latest version of UPX from the GitHub API.

    Returns:
        The latest version of UPX.
    """
    url = "https://api.github.com/repos/upx/upx/releases/latest"
    response = urllib.request.urlopen(url)
    data = json.load(response)
    return data["tag_name"]

def download_upx(url, output_file):
    """
    Downloads UPX from the given URL and saves it to the specified output file.

    Args:
        url: The URL of the UPX download.
        output_file: The path to the output file.
    """
    print("Downloading UPX archive...")
    print("URL:", url)
    print("Saving to:", output_file)
    response = urllib.request.urlopen(url)
    with open(output_file, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def extract_upx(input_file, output_dir, zip_name_dir):
    """
    Extracts the UPX archive to the specified output directory.

    Args:
        input_file: The path to the UPX archive.
        output_dir: The path to the output directory.
    """
    print("Extracting UPX archive...")
    if sys.platform == "darwin":
        print("macOS detected, using unzip command...")
        print(" ".join(["unzip", input_file, "-d", output_dir]))
        # macOS
        subprocess.check_call(["unzip", input_file, "-d", output_dir])
    else:
        # Linux or Windows
        print("Linux or Windows detected, using tar command...")
        print(" ".join(["tar", "-xf", input_file, "-C", output_dir]))
        subprocess.check_call(["tar", "-xf", input_file, "-C", output_dir])

    if os.path.exists(os.path.join(output_dir, zip_name_dir)):
        # Move the contents of output_dir/zip_name_dir to output_dir
        shutil.move(os.path.join(output_dir, zip_name_dir), output_dir)

    if sys.platform == "linux" or sys.platform == "darwin":
        print("setting executable permissions...")
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                os.chmod(file_path, 0o755)
        
def add_upx_to_path(upx_dir):
    """
    Adds the UPX directory to the PATH environment variable.

    Args:
        upx_dir: The path to the UPX directory.
    """
    if sys.platform == "windows":
        # Windows
        os.environ["PATH"] += os.pathsep + upx_dir
    else:
        # macOS or Linux
        os.environ["PATH"] += os.pathsep + os.path.join(upx_dir, "bin")

def main():
    """
    Downloads, extracts, and installs the latest version of UPX.
    """

    # Get the latest version of UPX
    latest_version = get_latest_upx_version()

    # Determine the system type
    system_type = sys.platform

    # Determine the UPX download URL
    if system_type == "darwin":
        sys.exit("MacOS is not supported yet.")
    elif system_type == "linux":
        # Linux
        if sys.maxsize > 2**32:
            # 64-bit
            file_name = f"upx-{latest_version[1:]}-amd64_linux"
            upx_url = f"https://github.com/upx/upx/releases/download/{latest_version}/{file_name}.tar.xz"
        else:
            # 32-bit
            file_name = f"upx-{latest_version[1:]}-i386_linux"
            upx_url = f"https://github.com/upx/upx/releases/download/{latest_version}/{file_name}.tar.xz"
    else:
        # Windows
        if sys.maxsize > 2**32:
            # 64-bit
            file_name = f"upx-{latest_version[1:]}-win64"
            upx_url = f"https://github.com/upx/upx/releases/download/{latest_version}/{file_name}.zip"
        else:
            # 32-bit
            file_name = f"upx-{latest_version[1:]}-win32"
            upx_url = f"https://github.com/upx/upx/releases/download/{latest_version}/{file_name}.zip"

    print(f"Installing UPX {latest_version}...")
    print(f"Downloading UPX from {upx_url}...")
    upx_url = "https://mirror.ghproxy.com/" + upx_url
    print("Proxy URL:", upx_url)

    # Download UPX
    upx_zip = "upx.zip"
    download_upx(upx_url, upx_zip)

    # Extract UPX
    upx_dir = "upx"
    if os.path.exists(upx_dir): shutil.rmtree(upx_dir)
    os.mkdir(upx_dir)
    extract_upx(upx_zip, upx_dir, file_name)

    # Add UPX to PATH
    add_upx_to_path(upx_dir)

    # Cleanup
    os.remove(upx_zip)

if __name__ == "__main__":
    main()
