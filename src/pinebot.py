from facebook_scraper import get_posts
import requests
import time
import logging
import json
import random
import datetime
# credentials=('pinoideabot', '-Xqm9_dBWm2dSXU'),
class Facebookbot:

    def __init__(self, credentials, database):
        self.credentials = credentials
        self.database = database

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

    def postdiscord(self, webhook_url, posts):
        for post in posts:
            try:
                payload = {"content": post}
                response = requests.post(webhook_url, json=payload)
                if response.status_code != 204:
                    raise Exception(f"Error posting to Discord: {response.text}")
            except Exception as e:
                logging.error(f"Error posting to Discord: {e}")

    def datapick(self, pages = None, groups = None, amount = 10):
        if not pages and not groups:
            raise ValueError("At least one account or group must be provided.")

        with open('db.txt', 'r', encoding='utf-8') as file:
            postlist = [eval(post_str) for post_str in file.readlines()]

        data = self.datascrape(pages, groups, amount)

        # Find the difference between the sets
        diff = [post for post in data if post['post_id'] != [old_post['post_id'] for old_post in postlist]]

        return diff

def main():
    # # ---- ---- ---- ---- # Configuration #
    pages = ['page1', 'page2', 'page3']
    groups = ['group1', 'group2']
    webhook_mapping = \
    {
        '#pinoidea': "[webhook_mapping_pinoidea]",
    }
    webhook_free = "[webhook_free]"

    bot_fb = Facebookbot(credentials = ('username', 'password'), database = 'db.txt')

    # # ---- ---- ---- ---- # Database #
    posts = bot_fb.datapick(pages = pages, groups = groups, amount = 1)
    
    with open('db.txt', 'a+', encoding='utf-8') as file:
        for post in posts:
            time.sleep(2)
            for string, webhook_url in webhook_mapping.items():
                try:
                    message = f"⏩          {post['post_url']}          ⏪ \n ```{post['text']}```"
                
                    if string in post['text'].lower():
                        bot_fb.postdiscord(webhook_url, message)
                        bot_fb.postdiscord(webhook_url, images)
                    else:
                        bot_fb.postdiscord(webhook_free, [message])
                        bot_fb.postdiscord(webhook_free, post['images_lowquality'])
                except:
                    logging.error(f"Error posting post to Discord")
            file.write('%s\n' % post)

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    main()
