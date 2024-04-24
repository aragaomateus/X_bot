import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dateutil import parser, tz
from dotenv import load_dotenv
import tweepy
import openai
import os 
import time
load_dotenv()

# Function to get the newest post from the RSS feed

# Now you can safely use the environment variable
OPENAI_KEY = os.environ.get('OPENAI_KEY')
# Tweepy authentication
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

openai.api_key = OPENAI_KEY
# Function to get the newest post from the RSS feed


client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

"""TODO
theres a problem when the latest tweet does not have 
text and the GPT cant actually have a context to reply for. 

"""
def get_newest_post(url):
    response = requests.get(url)
    response.raise_for_status()

    current_time_gmt = datetime.now(tz=tz.tzutc())
    tree = ET.fromstring(response.content)
    newest_post = None
    latest_time = datetime.min.replace(tzinfo=tz.tzutc())

    for element in tree.findall('.//item'):
        pub_date = element.find('pubDate').text if element.find('pubDate') is not None else None
        if pub_date:
            post_time_gmt = parser.parse(pub_date).astimezone(tz=tz.tzutc())
            if current_time_gmt - timedelta(minutes=25) <= post_time_gmt <= current_time_gmt:
                if post_time_gmt > latest_time:
                    latest_time = post_time_gmt
                    newest_post = element

    if newest_post:
        title = newest_post.find('title').text
        link = newest_post.find('link').text
        return title, link, latest_time
    else:
        return None

def post_tweet(content, tweet_id):
    try:
        response = client.create_tweet(text=content, in_reply_to_tweet_id=tweet_id)
        print(response)
        # print("Tweet posted successfully. Tweet ID:", response.data['id'])
        return response.data['id']
    except Exception as e:
        print(f"An error occurred: {e}")
        return e  # Returning None or a relevant error message instead of response in case of error




def generate_reply(prompt):
    response = openai.ChatCompletion.create(model="gpt-4",
        messages=[
      {"role": "system", "content": "You are a helpful assistant tweet replier. You craft tweet-sized replies(280 characters).No quotation marks, just text. No emojis, no hashtags,no mentions to the author of the tweet."},
      {"role": "user", "content": prompt}
    ])
    return response.choices[0].message.content

"""TODO
report how many runs the bot has done in the current time that it has been running.
DONE 
"""
def write_report(new_run, filename='report.txt'):
    with open(filename, 'w') as file:
        file.write("Report of Successful Tweets\n")
        file.write(f"Total Successful Posts: {len(new_run.replies)}\n")
        file.write(f"Total bot runs: {new_run.runs}\n")
        file.write(f"Avg Posts per Run: {len(new_run.replies)/new_run.runs}\n")
        file.write(f"# Replies Frequency per URL # \n")
        for k,v in new_run.url_count.items():
            file.write(f"{k} : {v}\n")

        file.write(f" # --------------------------------- # \n")
        for tweet_id in new_run.replies.keys():
            file.write(f"Replied to Tweet ID: {tweet_id}\n")
            file.write("tweet:"+new_run.replies[tweet_id][0]+"\n")
            file.write("link:"+new_run.replies[tweet_id][1]+"\n")
            file.write("timestamp:"+str(new_run.replies[tweet_id][2])+"\n")
            file.write("reply:"+new_run.replies[tweet_id][3]+"\n")
            file.write("--------------------------------"+"\n")




def log_message(message, file_path='automation_log.txt'):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {message}\n"
    with open(file_path, 'a') as log_file:
        log_file.write(log_entry)



def load_ids():
    list_of_ids =[]
    with open('replied_ids.txt', 'r') as file: 
        lines = file.readlines()
        for line in lines:
            list_of_ids.append(line.strip('\n'))
    
    return list_of_ids

def append_ids(id):
    with open('replied_ids.txt', 'a') as file: 
        file.write(id+'\n')
       
