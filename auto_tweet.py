import time
import emoji
import requests
import tweepy
import random
import pandas as pd
import datetime as dt
import smtplib
import openai
import regex as re
from decouple import config


class AutoTweeter:
    # Keys and Passwords
    API_KEY = config('API_KEY')
    API_KEY_SECRET = config('API_KEY_SECRET')
    ACCESS_TOKEN = config('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = config('ACCESS_TOKEN_SECRET')
    BEARER_TOKEN = config('BEARER_TOKEN')
    CLIENT_ID = config('CLIENT_ID')
    CLIENT_SECRET = config('CLIENT_SECRET')
    OPENAI_API_KEY = config('OPENAI_API_KEY')
    OPENAI_ORGANISATION_KEY = config('OPENAI_ORGANISATION_KEY')
    EMAIL = config('EMAIL')
    PASSWORD = config('PASSWORD')

    def __init__(self):
        self.client = tweepy.Client(consumer_key=self.API_KEY,
                                    consumer_secret=self.API_KEY_SECRET,
                                    access_token=self.ACCESS_TOKEN,
                                    access_token_secret=self.ACCESS_TOKEN_SECRET)

    # Post a single tweet

    def single_tweet(self, content):
        response = self.client.create_tweet(text=content)
        return response.data['id']

    # Post a twitter thread:

    def thread(self, content, num_of_tweets):
        first_tweet = self.client.create_tweet(text=content[0], )
        tweet_id = first_tweet.data['id']
        for i in range(1, num_of_tweets):
            tweet = self.client.create_tweet(in_reply_to_tweet_id=tweet_id,
                                             text=content[i], )
            tweet_id = tweet.data['id']
        return tweet_id

    def topic_of_the_day(self):
        branch_for_the_day = random.choices(
            ['entrepreneurship', 'marketing', 'copywriting'], weights=(33, 50, 10), k=1)[0]
        sheety_headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic cHJhbm5heTpwcmFubmF5QXV0aGVudGljYXRpb24=",
            "username": "prannay",
            "password": "prannayAuthentication",
        }
        sheety_base_url = f'https://api.sheety.co/cb582a96b98109c7051e483026c6e610/twitterAutomatedPosting/{branch_for_the_day}/2'
        topic_of_the_day = requests.get(
            url=sheety_base_url, headers=sheety_headers)
        print(topic_of_the_day.json())

        if topic_of_the_day.status_code == 404:
            with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
                connection.ehlo()
                connection.login(user=self.EMAIL, password=self.PASSWORD)
                connection.sendmail(from_addr=self.EMAIL, to_addrs="prannaykedia1@gmail.com",
                                    msg=f"Subject: {branch_for_the_day} Over!\n\n"
                                        f"Topic: Add more topics or remove the branch")
            return "business"
        else:
            response = requests.delete(
                url=sheety_base_url, headers=sheety_headers)
            print(f"Delete: {response}")
            return topic_of_the_day.json()[branch_for_the_day]['topic']

    # Update Sheet, Done Sheet, Send Mail

    def documentation(self, topic: str, content: list, today, tweet_id):
        content_string = ''
        for tweet in content:
            content_string += tweet + '\n'

        sheets_tweets_url = 'https://docs.google.com/spreadsheets/d/1tb9z14lyD7puJHpOSYB8IQhE5IKAZ2U_X-C6Rqhd2eE/edit#gid=0'
        sheety_endpoint = "https://api.sheety.co/cb582a96b98109c7051e483026c6e610/twitterAutomatedPosting/twitterPosts"
        sheety_headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic cHJhbm5heTpwcmFubmF5QXV0aGVudGljYXRpb24=",
            "username": "prannay",
            "password": "prannayAuthentication",
        }

        date = dt.datetime.today().strftime("%d/%m/%Y, %H:%M:%S")
        sheety_parameter = {
            "twitterpost": {
                "topic": topic,
                "content": content_string,
                "timestamp": date,
                "id": tweet_id,
            }
        }
        sheety_response = requests.post(
            url=sheety_endpoint, json=sheety_parameter, headers=sheety_headers)
        print(sheety_response.json())
        time.sleep(0.5)

        emojis_iter = map(lambda y: y, emoji.UNICODE_EMOJI['en'].keys())
        regex_set = re.compile('|'.join(re.escape(em) for em in emojis_iter))
        emoji_list = regex_set.findall(content_string)
        mail_string = ''
        for character in content_string:
            if character not in emoji_list:
                mail_string += character

        with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
            connection.ehlo()
            connection.login(user=self.EMAIL, password=self.PASSWORD)
            connection.sendmail(from_addr=self.EMAIL, to_addrs="prannaykedia1@gmail.com",
                                msg=f"Subject: Today's Tweet\n\n"
                                    f"Topic: {topic}\n\n"
                                    f"{mail_string}\n\n"
                                    f"Tweet ID: {tweet_id}\n"
                                    f"Tweets Sheet: {sheets_tweets_url}"
                                )

    def generate_tweet_content(self, topic, type):
        openai.organization = self.OPENAI_ORGANISATION_KEY
        openai.api_key = self.OPENAI_API_KEY
        if type == 'Thread':
            response = openai.Completion.create(engine="text-davinci-003",
                                                prompt=f"Generate an informative and engaging twitter thread of 5 tweets "
                                                f"with 5 relevant hashtags on the topic {topic}",
                                                max_tokens=2000,
                                                temperature=0.98,
                                                presence_penalty=1.2,
                                                frequency_penalty=1.2,
                                                best_of=4)
        else:
            response = openai.Completion.create(engine="text-davinci-003",
                                                prompt=f"Generate a quote for twitter with "
                                                f"trending keywords on the topic {topic}",
                                                max_tokens=800,
                                                temperature=0.5)
        text = response.choices[0]["text"]
        if text[:2] == '\n\n':
            text = text[2:]
        tweets = []
        tweet = ''
        for i in range(len(text)):
            character = text[i]
            if character == '\n' or i == len(text) - 1:
                if text[i - 1] != '\n':
                    tweets.append(tweet)
                    tweet = ''
            else:
                tweet += character
        for i in range(len(tweets)):
            tweet = tweets[i]
            try:
                first_number = int(tweet[0])
                tweet = tweet[1:]
                if tweet[1] == '.':
                    tweet = tweet[2:]
            except Exception:
                continue
            if tweet[0] == '.' or tweet[0] == '-':
                tweet = tweet[1:]
            tweet = tweet.strip()
            tweets[i] = tweet
        for tweet in tweets:
            emojis_iter = map(lambda y: y, emoji.UNICODE_EMOJI['en'].keys())
            regex_set = re.compile('|'.join(re.escape(em)
                                   for em in emojis_iter))
            num_emoji = len(regex_set.findall(tweet))
            num_character = num_emoji + len(tweet)
            if num_character > 260:
                self.generate_tweet_content(topic, type)
        return tweets

    def main(self):
        today = dt.datetime.now()
        time_now = today.now().time().strftime("%H:%M")
        print(time_now)
        if time_now == "12:00":  # 17:30 IST == 12:00 UTC
            print("Quotes")
            topic = random.choice(
                ['entrepreneurship', 'copywriting', 'personal finance', 'marketing'])
            content = self.generate_tweet_content(topic, 'Quote')
            tweet_id = self.thread(content, 1)
            self.documentation(topic=topic, content=content,
                               today=today, tweet_id=tweet_id)
            return "Quote"
        elif time_now == "06:00":  # 11:30 IST == 6:00 UTC
            print("Thread")
            # Get topic
            topic = self.topic_of_the_day()
            if topic == 0:
                self.documentation(topic="Topics Over", content=[
                    ''], today=today, tweet_id="")
                exit(0)
            # Generate Content
            content = self.generate_tweet_content(topic, "Thread")
            tweets = content.insert(0, f'{topic}\n\nA Thread👇🏼')
            content.append(
                'Follow @KediaPrannay & @WriteeAi for more such threads!\n\n#Writee #WriteeAI #WrittenWithWritee #www')
            number_of_tweets = len(content)
            # Tweet
            tweet_id = self.thread(content, number_of_tweets)
            print(f"Tweet ID: {tweet_id}")
            self.documentation(topic=topic, content=content,
                               today=today, tweet_id=tweet_id)
            return "Thread"
        else:
            return "Nothing Yet"
