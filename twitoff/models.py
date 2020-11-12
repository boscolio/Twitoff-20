"""SQLAlchemy models and utiliy functions for Twitoff Application"""

from flask_sqlalchemy import SQLAlchemy


DB = SQLAlchemy()


# User table
class User(DB.Model):
    """Twitter User Table that corresponds to tweets - SQLAlchemy syntax"""
    id = DB.Column(DB.BigInteger, primary_key=True)  # id column (primary key)
    name = DB.Column(DB.String, nullable=True) # name column
    # keeps track of recent user tweet
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return "<User: {}>".format(self.name)


class Tweet(DB.Model):
    """Tweet text data - associated with User Table"""
    id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Unicode(300))
    vect = DB.Column(DB.PickleType, nullable=False)
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey("user.id"), nullable=False)
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
        return"<Tweet: {}>".format(self.text)