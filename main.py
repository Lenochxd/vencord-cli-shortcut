import requests
import subprocess
import os
import sys

# Define the URL for the GitHub API and the local file paths
api_url = "https://api.github.com/repos/Vencord/Installer/releases/latest"
local_version_file = "vencord-cli/latest.txt"
download_url = "https://github.com/Vencord/Installer/releases/download/{}/VencordInstallerCli.exe"
download_path = "vencord-cli/VencordInstallerCli.exe"

# Function to get the latest version from GitHub
def get_latest_github_version():
    response = requests.get(api_url)
    response.raise_for_status()
    latest_release = response.json()
    return latest_release["tag_name"]

# Function to get the current local version
def get_local_version():
    with open(local_version_file, "r") as file:
        return file.read().strip()

# Function to update the local version file
def update_local_version(new_version):
    with open(local_version_file, "w") as file:
        file.write(new_version)

# Function to download the latest installer
def download_installer(version):
    url = download_url.format(version)
    response = requests.get(url)
    response.raise_for_status()
    with open(download_path, "wb") as file:
        file.write(response.content)

# Main logic
def main():
    temp_dir = os.getcwd()
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    latest_version = get_latest_github_version()
    local_version = get_local_version()

    if latest_version > local_version or not os.path.exists(download_path):
        print(f"Updating from version {local_version} to {latest_version}")
        update_local_version(latest_version)
        download_installer(latest_version)
        print("Update complete.")
    
    subprocess.run([download_path], check=True)
    os.chdir(temp_dir)

if __name__ == "__main__":
    main()