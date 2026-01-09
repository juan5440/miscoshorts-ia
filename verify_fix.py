import os
import imageio_ffmpeg
import subprocess
import shutil
import sys

# Simulate the logic in maker.py
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_exe

project_dir = os.path.dirname(os.path.abspath(__file__))
target_ffmpeg = os.path.join(project_dir, "ffmpeg.exe")

print(f"Project dir: {project_dir}")
print(f"Target ffmpeg: {target_ffmpeg}")

if not os.path.exists(target_ffmpeg):
    print(f"Copying ffmpeg to {target_ffmpeg}...")
    shutil.copyfile(ffmpeg_exe, target_ffmpeg)
else:
    print("ffmpeg.exe already exists.")

if project_dir not in os.environ["PATH"]:
    os.environ["PATH"] = project_dir + os.pathsep + os.environ["PATH"]

try:
    print("Trying execution from PATH...")
    # This should now work because we added project_dir to PATH and ffmpeg.exe is there
    subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("SUCCESS: ffmpeg found in PATH and executed successfully.")
except FileNotFoundError:
    print("FAILURE: ffmpeg not found in PATH.")
except Exception as e:
    print(f"FAILURE: Error executing ffmpeg: {e}")

# Cleanup for test (optional, but maybe good to leave it if it works)
# if os.path.exists(target_ffmpeg):
#    os.remove(target_ffmpeg)
