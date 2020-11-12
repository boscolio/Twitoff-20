"""Main app/routing file for Twitoff"""

from os import getenv
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_or_update_user
from .predict import predict_user

def create_app():
    """Create and configure instance of Flask application"""
    app = Flask(__name__)

    # database and app configurations
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # initializing database
    DB.init_app(app)

    # decorator for specific endpoint visits
    @app.route('/')
    def root():
        # renders base.html template, and passes title and users
        return render_template('base.html', title="home", users=User.query.all())

    @app.route('/compare', methods=["POST"])
    def compare():
        user0, user1 = sorted(
            [request.values['user1'], request.values['user2']])
        if user0 == user1:
            message = "Cannot compare users to themselves!"
        else:
            prediction = predict_user(user0, user1, request.values['tweet_text'])
            message = '{} is more likely to be said by {} than {}'.format(
                request.values["tweet_text"], user1 if prediction else user0,
                user0 if prediction else user1
            )
        
        return render_template('prediction.html', title="Prediciton", message=message)
    
    @app.route('/user', methods=["POST"])
    @app.route('user/<name>', methods=["GET"])
    def user(name=None, message=''):
        name = name or request.values["user_name"]
        try:
            if request.method == "POST":
                add_or_update_user(name)
                message = "User {} was successfully added!".format(name)

            tweets = User.query.filter(User.name == name).one().tweets

        except Exception as e:
            message = "Error adding {}: {}".format(name, e)
            tweets = {}
    
        return render_template("user.html", title="Home", users=User.query.all())

    @app.route('/update')
    def update():
        insert_example_users()
        return render_template('base.html', title="Home", users=User.query.all())

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title="Home")
    
    return app

def insert_example_users():
    add_or_update_user('elonmusk')
    add_or_update_user('nasa')