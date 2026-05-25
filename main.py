import json
import os
from pathlib import Path
import random
import re
import time

from dotenv import load_dotenv
from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi


VIDEO_INFO_JSON_FILENAME = "ah_vid_info.json"


def generate_file():
    try:
        load_dotenv()
        with open(os.getenv("HISTORY_JSON_PATH")) as file:
            data = json.load(file)
    except FileNotFoundError:
        print("The file was not found.")
    except json.JSONDecodeError:
        print("Error: The file contains invalid JSON.")

    youtube_video_links = set(
        [mini["url"].split("&list")[0] for mini in data["Browser History"] if "youtube.com/watch" in mini["url"]]
    )

    make_json(youtube_video_links)


def make_vid_info_dict(youtube: YouTube, link):
    vid_title = youtube.title
    vid_id = link.split("watch?v=")[1]
    
    return {
        "title": vid_title,
        "link": link,
        "vid_id": vid_id
    }


def make_json(links):
    ah_links = []
    broken_ah_links = []

    for link in links:
        try:
            youtube = YouTube(link)

            if youtube.author == "Alex Hormozi":
                vid_info = make_vid_info_dict(youtube, link)
                ah_links.append(vid_info)
        except Exception as ex:
            success = False
            retries = 0

            while retries < 3:
                print(f"Try #{retries+1} on {link}")
                try:
                    youtube = YouTube(link)

                    if youtube.author == "Alex Hormozi":
                        vid_info = make_vid_info_dict(youtube, link)
                        ah_links.append(vid_info)

                    success = True
                    break
                except Exception as e:
                    retries += 1
                    time.sleep(5)

            if not success:
                print(f"Skipping link - {link}: {ex}")
                broken_ah_links.append(link)

    if len(broken_ah_links) > 0:
        with open("links_with_errors.txt", "w") as file:
            file.write("Here are the links that gave errors:\n")
            file.writelines("\n".join(broken_ah_links))

    with open(VIDEO_INFO_JSON_FILENAME, "w") as file:
        json.dump(ah_links, file, indent=4)


def make_transcript_file(vid_info_dict):
    ytt_api = YouTubeTranscriptApi()
    fetched_transcript = ytt_api.fetch(vid_info_dict["vid_id"])

    with open(f"transcripts/{vid_info_dict["title"]}.txt", "w") as file:
        for snippet in fetched_transcript:
            file.write(f"{snippet.start} - {snippet.start + snippet.duration}: {snippet.text}\n")

    time.sleep(random.randint(60, 120))


def search():
    path = Path('transcripts/')
    for file in path.glob('*.txt'):
        print(f"Processing {file.name}!")
        with file.open('r') as f:
            transcript = [line.strip() for line in f.readlines() if line.strip()]

            for line in transcript:
                if re.search(r'\bembrace\b', line) or re.search(r'\buncertainty\b', line):
                    print(f"{file.name}\n\t{line}")


def main():
    try:
        with open(VIDEO_INFO_JSON_FILENAME) as file:
            api_json = json.load(file)
    except FileNotFoundError:
        generate_file()
        with open(VIDEO_INFO_JSON_FILENAME) as file:
            api_json = json.load(file)
        time.sleep(120)
    except json.JSONDecodeError:
        print("Error: The file contains invalid JSON.")

    Path("transcripts/").mkdir(exist_ok=True)

    for video_info_dict in api_json:
        if not Path(f"transcripts/{video_info_dict["title"]}.txt").is_file():
            make_transcript_file(video_info_dict)
        else:
            print(f"File \"transcripts/{video_info_dict["title"]}.txt\" already exists!")

    search()


main()
