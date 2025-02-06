import json 
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os 
from confluent_kafka import Producer
import praw
import datetime

# Load environment variables from the .env file
load_dotenv()

# Kafka Producer Configuration (Inside Docker Network)
KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
producer_config = {
    'bootstrap.servers': KAFKA_BROKERS,
    'acks': 'all',  # Ensures all brokers acknowledge writes
    'retries': 5     # Retry in case of failure
}
producer = Producer(producer_config)

# Create a new Reddit client
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET= os.environ['CLIENT_SECRET']
REDDIT_USERNAME= os.environ['REDDIT_USERNAME']
REDDIT_SECRET= os.environ['REDDIT_SECRET']
USER_AGENT = os.environ['USER_AGENT']

# load praw Reddit
reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        password=REDDIT_SECRET,
        user_agent=USER_AGENT ,
        username=REDDIT_USERNAME,
)

# Load subreddits to follow, keywords, etc.
with open('redditAPI/follow_config.json', 'r') as file:
    data_to_track = json.load(file)
subreddit_names = data_to_track["subreddit_names"]
keywords_dict = data_to_track["keywords_dict"]

# Initialize FastAPI app
app = FastAPI(
    title="Reddit API",
    description="API that tracks topics, comments, and replies of predefined subreddits related to crypto",
    version="1.0.0"
)

@app.get("/health_check", summary="Health Check", tags=["Monitoring"])
async def health_check():
    """
    Checks if the application is running and functional.
    """
    return {
        "status": "success",
        "message": "Health check successful."
    }

@app.post("/send_data")
async def send_data(start_date : str, end_date : str):
    """
        - start_date (str) : 'DD/MM/YYYY'
        - end_date (str) : 'DD/MM/YYYY' 

        return post, its comments, replies of catch comments which were add to reddit between end_date (equals) and start_date (equals)
    """
    # Define target start and end dates
    start_date_dt_date = datetime.datetime.strptime(start_date, "%d/%m/%Y").date()
    end_date_dt_date = datetime.datetime.strptime(end_date, "%d/%m/%Y").date()
    date_today = datetime.datetime.today().date()
    if end_date_dt_date > date_today:
        raise HTTPException(status_code=422, detail=f"End date input ('{end_date_dt_date}') must be smaller than or equal to {date_today} !")
    
    
    total_posts, total_comments, total_replies = 0, 0, 0
    try:
        for subreddit_name in subreddit_names:
            for subject, keywords in keywords_dict.items():
                # retrieve posts
                scope_query = ' OR '.join(keywords)  # Combine keywords using OR
                # Get the subreddit instance
                subreddit = reddit.subreddit(subreddit_name)
                # 1. query 
                query_posts = subreddit.search(scope_query, sort='new', limit=None)
                for post in query_posts:
                    submission_date = datetime.datetime.utcfromtimestamp(post.created)
                    # we reached the limit date, we stop here !
                    if submission_date.date() < end_date_dt_date:
                        return {
                            "status": f"success, reached end_date: {submission_date.date()}",
                            "result": {
                                "total_post_add": total_posts,
                                "total_comments_add": total_comments,
                                "total_replies_add": total_replies
                            }
                        }
                    elif submission_date.date() > start_date_dt_date:
                        continue       
                    post_obj = {
                        "subreddit_name" : subreddit_name,
                        "post_id": post.id,
                        "subject" : subject,
                        "title": post.title,
                        "text": post.selftext,
                        "number_of_comments": post.num_comments,
                        "score": post.score,  # Fixed key name
                        "submission_date": submission_date.strftime("%d/%m/%Y, %H:%M:%S"),
                        "author_name": post.author.name,  # Renamed to avoid duplicate keys
                        "author_id": post.author.id if hasattr(post.author, 'id') else None,   
                    }
                    # produce to kafka 'posts' topic
                    producer.produce("posts", key=str(post_obj["post_id"]), value=json.dumps(post_obj))
                    total_posts += 1

                    # 2. comments 
                    for comment in post.comments.list():
                        comment_key = f"{post.id}_{comment.id}"

                        # 3. replies
                        replies = comment.replies.list()
                        for reply in replies:
                            reply_obj = {
                                "reply_id": reply.id,
                                "comment_id": comment.id,
                                "text": reply.body,
                                "score": reply.score,
                                "submission_date": datetime.datetime.utcfromtimestamp(reply.created).strftime("%d/%m/%Y, %H:%M:%S"),
                                "author": reply.author.name if reply.author else None,
                                "author_id": reply.author.id if hasattr(reply.author, 'id') else None                           
                            }
                            # produce to kafka 'replies' topic
                            reply_key = f"{comment_key}_{reply.id}"
                            producer.produce("replies", key=reply_key, value=json.dumps(reply_obj))
                            total_replies += 1

                        # finally treat comment and add also number_of_replies
                        comment_obj = {
                            "comment_id": comment.id,
                            "post_id": post.id,       
                            "text": comment.body,
                            "number_of_replies": len(replies),
                            "score": comment.score,
                            "submission_date": datetime.datetime.utcfromtimestamp(comment.created).strftime("%d/%m/%Y, %H:%M:%S"),
                            "author_name": comment.author.name if comment.author else None,
                            "author_id": comment.author.id if hasattr(comment.author, 'id') else None      
                        }
                        # produce to kafka 'comments' topic    
                        producer.produce("comments", key=comment_key, value=json.dumps(comment_obj))
                        total_comments += 1

        return {
            "status": "success",
            "result": {
                "total_post_add": total_posts,
                "total_comments_add": total_comments,
                "total_replies_add": total_replies
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
   