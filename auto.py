import bot_function as bf
import time

# defining a class that will hold all of the information about the current run

class Run: 
    def __init__(self):
        self.replied_ids = []
        self.runs = 0
        self.replies = {}
        self.url_count={}

# list of feed URL to inspect 
urls = [
        "https://rss.app/feeds/nF0z0htIiSicmtEI.xml",
        "https://rss.app/feeds/ukk7rZTH4VMxByUk.xml",
        "https://rss.app/feeds/ekrmgWuZaXTNI2pA.xml",
        "https://rss.app/feeds/DivJ2iYw7KOcsGK6.xml",
        "https://rss.app/feeds/Sh6a8c7kumlSaOAc.xml",
        "https://rss.app/feeds/HkyNl9eeYDOrUBxr.xml",
        "https://rss.app/feeds/SfagktHZw5X11tlY.xml",
        "https://rss.app/feeds/ifLDZNGwTtgA57Wu.xml",
        "https://rss.app/feeds/1ElygOT0SPNp00TF.xml",
        "https://rss.app/feeds/ojZJT6ZJQFN2w7WS.xml",
        "https://rss.app/feeds/iqARUd9IHBFbuShi.xml",
        "https://rss.app/feeds/QmEwcspSuCZghzNk.xml",
        "https://rss.app/feeds/tuSrvEAiVTQKiD3E.xml",
        "https://rss.app/feeds/vSNaiVozufykpACx.xml",
        "https://rss.app/feeds/2pJDwWu8v7gnPiD4.xml",
        "https://rss.app/feeds/X1ZZIDgoJsCCd1pf.xml",
        "https://rss.app/feeds/GpMvwB5mw13I4hH2.xml",
        "https://rss.app/feeds/I9YtRS6U9dZUMwBW.xml",
        "https://rss.app/feeds/Z4vIsOE4SX7ve1hH.xml",
        "https://rss.app/feeds/WhXgkSgFIqQ7eOKZ.xml"
        ]

# Main loop
new_run = Run()
successful_posts = 0
too_many = False
tweet_id_history = bf.load_ids()

try:
    timestamp_start = time.strftime("%Y-%m-%d %H:%M:%S")
    log_path = f'./logs/automation_log_{timestamp_start}.txt'
    report_path = f'./reports/report_{timestamp_start}.txt'


    bf.log_message("------RUN: "+timestamp_start+"-----",file_path=log_path)
    while successful_posts < 49:
        new_run.runs+=1
        for url in urls:
            newest_post = bf.get_newest_post(url)
            bf.log_message("CHECKING url:"+url,file_path=log_path)
            if newest_post:
                title, link, timestamp = newest_post
                tweet_id = link.split('/')[-1]  # Extract tweet ID from link

                if tweet_id not in new_run.replied_ids and tweet_id not in tweet_id_history:

                    new_run.replies[tweet_id] = [title,link,timestamp]
                    bf.log_message("REPLYING to tweet:"+ tweet_id,file_path=log_path)
                    
                    prompt = f"""Create a tweet-sized(280 characters)(3 short sentences max) reply to the 
                    following Tweet post, No emojis allowed, 
                    no mentions to the author of the tweet:'{title}'"""
                    tweet_reply = bf.generate_reply(prompt)

                    # tweet_reply = "A dummy reply for testing"
                    new_run.replies[tweet_id].append(tweet_reply)
                    bf.append_ids(tweet_id)
                    try:
                        response_id = bf.post_tweet(tweet_reply, tweet_id)
                        # response_id = 'id'
                        if type(response_id) == str:
                            new_run.replied_ids.append(tweet_id)
                            bf.log_message(f'SUCCESSFUL REPLY: '+ response_id,file_path=log_path)

                            if url in new_run.url_count:
                                new_run.url_count[url]+=1
                            else: 
                                new_run.url_count[url] = 1

                            successful_posts += 1
                            time.sleep(25)
                        elif 'Too Many Requests' in str(response_id):
                            too_many = True
                            bf.log_message(f'ERROR >>> BREAKING: Error posting tweet: {response_id}',file_path=log_path)
                            break
                        elif "400 Bad Request" in str(response_id):
                            bf.log_message(f'ERROR >>> BAD Request: Error posting tweet: {response_id}',file_path=log_path)
                            break
                        elif " 403 Forbidden" in str(response_id) :
                            bf.log_message(f'ERROR >>> Forbidden  Request: Error posting tweet: {response_id}',file_path=log_path)
                            break
                        else:
                            break
                    except Exception as e:
                        bf.log_message(f'ERROR posting tweet: {e}',file_path=log_path)
                else:
                    bf.log_message('Already replied to this tweet',file_path=log_path)
            else:
                bf.log_message("No new posts found in the last 25 minutes.",file_path=log_path)
        
        #make sure to brake the whole process otherwise we will be wasting the GPT 4 credits
        if too_many: 
            bf.write_report(new_run,report_path)
            break
        # Wait for 30 minutes before the next iteration
        bf.log_message("SLEEPING: for 30 min",file_path=log_path)
        bf.write_report(new_run,report_path)

        time.sleep(1500)
except KeyboardInterrupt:
    print("Process interrupted by user.")
    # Write report at the end of the process or if interrupted
