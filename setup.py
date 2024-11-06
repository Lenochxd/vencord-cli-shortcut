from cx_Freeze import setup, Executable
import subprocess
import os
import sys
import shutil
import uuid
import time

def sign_executable(file_path):
    signtool_path = r"C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe"
    timestamp_url = "http://timestamp.digicert.com"
    command = [
        signtool_path,
        "sign",
        "/a",
        "/fd", "SHA256",
        "/tr", timestamp_url,
        "/td", "SHA256",
        file_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to sign {file_path}: {result.stderr}")
    else:
        print(f"Successfully signed {file_path}")

def zip_build(build_dir):
    # Create a temporary directory outside the build directory to hold the build directory with the desired structure
    portablebuild_dir = "PortableBuild"
    os.makedirs(portablebuild_dir, exist_ok=True)

    # Move the build directory into the temporary directory
    shutil.move(build_dir, portablebuild_dir)

    # Rename the directory inside PortableBuild
    final_dir = "PortableBuild"
    inner_dir = os.path.join(portablebuild_dir, os.listdir(final_dir)[0])
    new_inner_dir = os.path.join(final_dir, "vencordinstall")
    os.rename(inner_dir, new_inner_dir)

    # Create a zip file of the temporary directory
    zip_file = shutil.make_archive('vencordinstall-win-amd64-portable', 'zip', final_dir)

    # Move the zip file to the /dist directory
    dist_dir = "dist"
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    shutil.move(zip_file, os.path.join(dist_dir, os.path.basename(zip_file)))

    # Remove the PortableBuild directory
    shutil.rmtree(final_dir)

    print(f"Portable build zipped as '{os.path.join(dist_dir, os.path.basename(zip_file))}'")


if __name__ == "__main__":
    start_time = time.time()
    
    # Define the executable
    executables = [
        Executable(
            "main.py",
            base="Console",
            target_name="vencordinstall"
        )
    ]

    # Define the build options
    build_exe_options = {
        "packages": [],
        "includes": [],
        "include_files": [
            "README.md",
            "version.txt",
            ("vencord-cli\\latest.txt", ".\\vencord-cli\\latest.txt")
        ],
        "excludes": ["cx_Freeze"],
        "include_msvcr": False,
    }

    # Define the MSI options
    bdist_msi_options = {
        "upgrade_code": f"{{{uuid.uuid4()}}}",
        "add_to_path": True,
        "summary_data": {
            "author": "LenochJ",
            "comments": "This script checks for the latest version of Vencord Installer and updates it if necessary.",
            "keywords": "Vencord, Installer, Update, GitHub, Version Check",
        }
    }

    # Setup the cx_Freeze script
    with open("version.txt") as f:
        version = f.read().strip()

    setup(
        name="vencordinstall",
        version=version,
        description="A script to check for the latest version of Vencord Installer and update it if necessary. ALL CREDITS FOR VENCORD TO VENDICATED.",
        author_email="contact.lenoch@gmail.com",
        options={
            "build_exe": build_exe_options,
            "bdist_msi": bdist_msi_options
        },
        executables=executables
    )
    
    
    build_dir = f"build/exe.win-amd64-{sys.version_info.major}.{sys.version_info.minor}"
    
    # Sign the main executable
    sign_executable(os.path.join(build_dir, "vencordinstall.exe"))
    
    
    # Zip the build directory
    zip_build(build_dir)
    
    # Rename the MSI file to remove the version from it
    msi_file = f"dist/vencordinstall-{version.removeprefix('v')}-win64.msi"
    new_msi_file = "dist/vencordinstall-win64.msi"
    if os.path.exists(msi_file):
        os.rename(msi_file, new_msi_file)
        print(f"Renamed MSI file to '{new_msi_file}'")
    else:
        print(f"MSI file '{msi_file}' not found")
    
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    
    print(f"Build done! {minutes}m {seconds}s")