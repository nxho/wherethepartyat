from instagrapi import Client
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag
from dotenv import load_dotenv
import json
import datetime
import os

load_dotenv()

IG_USERNAME = os.getenv('IG_USERNAME')
IG_PASSWORD = os.getenv('IG_PASSWORD')

path_to_stories = "/Users/babydeepthought/Documents/ncharge2/extensions/pyscraper/stories"

def try_login():
    try:
        cl = Client(json.load(open('creds.json')))
    except:
        cl = Client()
        cl.login(IG_USERNAME, IG_PASSWORD)
        json.dump(cl.get_settings(), open('creds.json', 'w'))

    return cl

def instantiate_user_data():
    with open("list.txt", "r") as file, open("accountdata.txt", "w") as file2:
        for line in file:
            username = line.strip()  # Remove leading/trailing whitespace and newline characters
            # Do something with the username
            print("Processing username:", username)
            user_id = cl.user_id_from_username(username)
            file2.write(f"{username},{user_id}")

def pull_stories():
    with open("accountdata.txt") as file:
        for line in file:
            line = line.strip()
            if len(line) == 0:
                break
            username, user_id = line.split(',')
            storieslist = cl.user_stories(user_id)
            print(f"Found {len(storieslist)} stories for username: {username}")
            for story in storieslist:
                print("Processing story for username:", username)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
                cl.story_download_by_url(story.thumbnail_url, f"{username};{timestamp}", path_to_stories)

if __name__ == "__main__":
    cl = try_login()
    pull_stories()
    print("Done!")
