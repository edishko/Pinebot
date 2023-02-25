from facebook_scraper import get_posts
import requests
import time
import logging
import json
import random
import datetime

def datascraper(credentials, accounts=None, groups=None, pages=None):
    if not accounts and not groups:
        raise ValueError("At least one account or group must be provided.")

    postlist = []

    # Scrape posts from groups
    if groups:
        for group in groups:
            try:
                for post in get_posts(group=group, pages=pages, credentials=credentials):
                    if post['post_id'] not in [p['post_id'] for p in postlist]:
                        postlist.append(post)
            except Exception as e:
                print(f"Error scraping posts from group {group}: {e}")

    # Scrape posts from accounts
    if accounts:
        for account in accounts:
            try:
                for post in get_posts(account=account, pages=pages, credentials=credentials):
                    if post['post_id'] not in [p['post_id'] for p in postlist]:
                        postlist.append(post)
            except Exception as e:
                print(f"Error scraping posts from account {account}: {e}")

    return postlist

def post_to_discord(webhook_url, post):
    try:
        payload = {"content": post}
        response = requests.post(webhook_url, json=payload)
        if response.status_code != 204:
            raise Exception(f"Error posting to Discord: {response.text}")
    except Exception as e:
        logging.error(f"Error posting to Discord: {e}")

def main():
    
    # ---- ---- ---- ---- # Configuration #
    accounts = ['pinoidea']
    groups = ['trainings.and.more','970175383682143']
    webhook_mapping = \
    {
        '#pinoidea': "https://discord.com/api/webhooks/1073996164002750564/dYIEg4xjxDZ-ujA5KL38_BYkS5Nj_xpOAEUy2cIvKYB7rZZ96BnF4TgcXvaTC3uzzZX0",
    }
    webhook_free = "https://discord.com/api/webhooks/1073993194615881779/xORBrcLu4md0it9zG5ObDmKk1QcDyxKuQRqcYxYQcvvjrZQAunixr60Jm-bBqtHZKtQz"
    # ---- ---- ---- ---- # Database #
    postlist = []
    with open('db.txt', 'r', encoding='utf-8') as file:
        postlist = [eval(post_str) for post_str in file.readlines()]

    data = datascraper(credentials=('pinoideabot', '-Xqm9_dBWm2dSXU'), accounts=accounts, groups=groups, pages=1)

    # Find the difference between the sets
    diff = [post for post in data if post['post_id'] not in [old_post['post_id'] for old_post in postlist]]

    with open('db.txt', 'a+', encoding='utf-8') as file:
        
        for post in diff:
            time.sleep(2)
            for string, webhook_url in webhook_mapping.items():
                try:
                    if string in post['text'].lower():
                        post_to_discord(webhook_url, f"⏩          {post['post_url']}          ⏪\n{post['text']}\n")
                        for image in post['images_lowquality']:
                            post_to_discord(webhook_url, post['link'])
                        post_to_discord(webhook_url, image)
                    else:
                        post_to_discord(webhook_free, f"⏩          {post['post_url']}          ⏪\n{post['text']}\n")
                        for image in post['images_lowquality']:
                            post_to_discord(webhook_free, image)
                        post_to_discord(webhook_free, post['link'])
                except:
                    logging.error(f"Error posting post to Discord")
            file.write('%s\n' % post)
            
if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    main()