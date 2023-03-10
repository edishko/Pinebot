# ---- ---- ---- ---- # Libaries #
from facebook_scraper import get_posts
import requests
import time
import logging
import json
import random
import datetime

# ---- ---- ---- ---- # Class #
class Facebookbot:

    def __init__(self, database, credentials = None):
        self.credentials = credentials
        self.database = database

        try:
            with open(self.database) as f:
                pass
        except FileNotFoundError:
            with open(self.database, "w") as f:
                pass

    def datascrape(self, pages = None, groups = None, amount = 10):
        if not pages and not groups:
            raise ValueError("At least one account or group must be provided.")

        postlist = []

        # Scrape posts from groups & pages
        if groups:
            for group in groups:
                try:
                    for post in get_posts(group = group, pages = amount, credentials = self.credentials):
                        if post['post_id'] not in [temp_post['post_id'] for temp_post in postlist]:
                            postlist.append(post)
                except Exception as e:
                    print(f"Error scraping posts from group {group}: {e}")

        if pages:
            for page in pages:
                try:
                    for post in get_posts(account = page, pages = amount, credentials = self.credentials):
                        if post['post_id'] not in [temp_post['post_id'] for temp_post in postlist]:
                            postlist.append(post)
                except Exception as e:
                    print(f"Error scraping posts from page {page}: {e}")

        return postlist

    def postdiscord(self, webhook_url, post):
        try:
            payload = {"content": post}
            response = requests.post(webhook_url, json=payload)
            if response.status_code != 204:
                raise Exception(f"Error posting to Discord: {response.text}")
        except Exception as e:
            logging.error(f"Error posting to Discord: {e}")

    def remove_duplicates(self, dicts, keys):
        seen = set()
        new_list = []
        for d in dicts:
            values = tuple(d[k] for k in keys)
            if values not in seen:
                seen.add(values)
                new_list.append(d)
        return new_list

    def datapick(self, pages = None, groups = None, amount = 10):
        if not pages and not groups:
            raise ValueError("At least one account or group must be provided.")

        with open(self.database, 'r', encoding='utf-8') as file:
            postlist = [eval(post_str) for post_str in file.readlines()]

        data = self.datascrape(pages, groups, amount)

        # Find the difference between the sets
        diff = [post for post in data if post['post_id'] not in [old_post['post_id'] for old_post in postlist]]
     
        # define a helper function to extract the value of a given key from a dictionary
        def get_dict_value(d, key):
            return d[key]

        # remove duplicates based on the 'name' key
        diff = list({get_dict_value(d, 'text'): d for d in diff}.values())

        return diff
# ---- ---- ---- ---- # Main #
def main():
    # ---- ---- ---- ---- # Configuration #
    database = 'db.txt'
    pages = ['page1', 'page2', 'page3']
    groups = ['group1', 'group2', 'group3']
    webhook_mapping = \
    {
        '#pinoidea': "[pinoideahook]",
    }
    webhook_free = "[freehook]"

    bot_fb = Facebookbot(database = database, credentials= ('username', 'password'))

    # ---- ---- ---- ---- # Database #
    posts = bot_fb.datapick(pages = pages, groups = groups, amount = 1)

    with open(database, 'a+', encoding='utf-8') as file:
        
        for post in posts:
            time.sleep(2)
            for string, webhook_url in webhook_mapping.items():
                try:
                    message = f"???          {post['post_url']}          ??? \n ```{post['text']}```"

                    if string in post['text'].lower():
                        bot_fb.postdiscord(webhook_url, message)
                        for image in post['images_lowquality']:
                            bot_fb.postdiscord(webhook_url, image)
                    else:
                        bot_fb.postdiscord(webhook_free, message)
                        for image in post['images_lowquality']:
                            bot_fb.postdiscord(webhook_free, image)
                except:
                    logging.error("Error posting post to Discord")
            file.write('%s\n' % post)

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    main()