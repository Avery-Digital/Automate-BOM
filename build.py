"""
Build script for BOM Auto-Populator standalone executable.

Usage:
    python build.py

Output:
    dist/BOM_Auto_Populator/  - Folder containing the standalone application
"""
import subprocess
import sys
import os

def build():
    project_dir = os.path.dirname(os.path.abspath(__file__))

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', 'BOM_Auto_Populator',
        '--windowed',
        '--onedir',
        '--collect-all', 'customtkinter',
        '--add-data', f'{os.path.join(project_dir, "core")};core',
        '--add-data', f'{os.path.join(project_dir, "gui")};gui',
        '--noconfirm',
        '--clean',
        os.path.join(project_dir, 'main.py'),
    ]

    print("Building BOM Auto-Populator...")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=project_dir)

    if result.returncode == 0:
        dist_path = os.path.join(project_dir, 'dist', 'BOM_Auto_Populator')
        print()
        print("=" * 60)
        print("Build successful!")
        print(f"Output: {dist_path}")
        print()
        print("To distribute:")
        print("  1. Zip the 'dist/BOM_Auto_Populator' folder")
        print("  2. Share the zip file")
        print("  3. Users extract and run BOM_Auto_Populator.exe")
        print("=" * 60)
    else:
        print("Build failed!")
        sys.exit(1)

if __name__ == '__main__':
    build()
