import os
from dotenv import load_dotenv
import praw
import datetime
import logging

logging.basicConfig(level=logging.DEBUG)

# Load environment variables from the .env file
load_dotenv()
# Set up your Reddit API credentials
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET= os.environ['CLIENT_SECRET']
REDDIT_USERNAME= os.environ['REDDIT_USERNAME']
REDDIT_SECRET= os.environ['REDDIT_SECRET']
USER_AGENT = os.environ['USER_AGENT']


class RedditClient:
    def __init__(self):
        self.reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        password=REDDIT_SECRET,
        user_agent=USER_AGENT ,
        username=REDDIT_USERNAME,
        )

    

    def queryBySubredditNameAndByKeywords(self, subreddit_name : str, subject : str, keywords : list, limit : int):
        scope_query = ' OR '.join(keywords)  # Combine keywords using OR
        # Get the subreddit instance
        subreddit = self.reddit.subreddit(subreddit_name)
        # Retrieve top 10 hot posts containing any of the keywords
        try:
            query_submissions = subreddit.search(scope_query, sort='hot', limit=limit)
        except Exception as e:
            # normalement openAI.BadRequestError
            raise f"Failed to fetch submissions: {str(e)}"

        submissions = [
            {
                "subreddit_name" : subreddit_name,
                "submission_id": submission.id,
                "subject" : subject,
                "title": submission.title,
                "text": submission.selftext,
                "number_of_comments": submission.num_comments,
                "score": submission.score,  # Fixed key name
                "submission_date": datetime.datetime.utcfromtimestamp(submission.created).strftime("%d/%m/%Y, %H:%M:%S"),
                "author_name": submission.author.name,  # Renamed to avoid duplicate keys
                "author_id": submission.author.id if hasattr(submission.author, 'id') else None,
                
            } for submission in query_submissions
        ]

        return submissions

    def queryCommentsBySubmissionId(self, submission_id: str):
        """
        Retrieve all comments for a given submission ID.
        """
        try:
            # Fetch the submission object using the ID
            submission = self.reddit.submission(id=submission_id)
            submission.comments.replace_more(limit=None)  # Replace "more comments" to get all comments
            comments = [
                {
                    "submission_id": submission_id,
                    "comment_id": comment.id,
                    "text": comment.body,
                    "score": comment.score,
                    "submission_date": datetime.datetime.utcfromtimestamp(comment.created).strftime("%d/%m/%Y, %H:%M:%S"),
                    "author_name": comment.author.name if comment.author else None,
                    "author_id": comment.author.id if hasattr(comment.author, 'id') else None      
                }
                for comment in submission.comments.list()  # Flatten all comments into a list
            ]
            return comments

        except Exception as e:
            raise f"Failed to fetch comments: {str(e)}"


    def queryRepliesCommentId(self, comment_id: str):
            """
            Retrieve all replies to a specific comment in a Reddit post by submission_id and comment_id.
            """
            try:
                comment = self.reddit.comment(comment_id)
                comment.refresh()
                replies = comment.replies.list()
                replies_list = []
               
                for reply in replies:
                    try:
                        reply_data = {
                            "comment_id": comment.id,
                            "reply_id": reply.id,
                            "text": reply.body,
                            "score": reply.score,
                            "submission_date": datetime.datetime.utcfromtimestamp(reply.created).strftime("%d/%m/%Y, %H:%M:%S"),
                            "author": reply.author.name if reply.author else None,
                            "author_id": reply.author.id if hasattr(reply.author, 'id') else None                           
                        }
                        replies_list.append(reply_data)
                    except Exception as e:
                        logging.info(f'reply {reply})')
                        logging.info(f'error {e})')

                return replies_list
            except Exception as e:
                raise f"Failed to fetch replies: {str(e)}"
            