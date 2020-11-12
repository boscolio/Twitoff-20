"""Retrieve tweets and users, then create embeddings and populate DB"""
from os import getenv
import spacy
import tweepy
from .models import DB, Tweet, User

#TODO - Don't have raw secrets in our code (create .env file)
TWITTER_API_KEY = getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = getenv("TWITTER_API_KEY_SECRET")
TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
TWITTER = tweepy.API(TWITTER_AUTH)

# nlp model
nlp = spacy.load('my_model')


def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector


def add_or_update_user(username):
    try:
        # grabs users from twitter DB
        twitter_user = TWITTER.get_user(username)
        # add or update user
        db_user = (User.query.get(twitter_user.id)) or (User(
            id=twitter_user.id, name=username))
        DB.session.add(db_user)

        # grabs tweets from twitter_user
        tweets = twitter_user.timeline(
            count=200, exclude_replies=True, include_rts=False,
            tweet_mode="extended"
        )

        # adds newest tweet to db_user.newest_tweet_id
        if tweets:
            db_user.newest_tweet_id = tweets[0].id


        for tweet in tweets:
            # stores vectorized representations of tweets
            vectorize_tweet = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id, text=tweet.full_text,
                             vect=vectorize_tweet)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    
    except Exception as e:
        # prints error to user and raises throughout app
        print('Error processsing {}: {}'.format(username, e))
        raise e

    # commit changes after try completes
    else:
        DB.session.commit()