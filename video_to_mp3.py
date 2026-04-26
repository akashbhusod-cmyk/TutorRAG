# Converts the videos to mp3
import os
import subprocess

files = os.listdir('Videos')

for file in files:
    tutorial_number = file.split(" ")[0].replace("#", "")
    title = file.split(" ", 1)[1].split(" [")[0]
    print(tutorial_number, title)
    subprocess.run(["ffmpeg", "-i", f"videos/{file}", f"audios/{tutorial_number}_{title}.mp3"])
