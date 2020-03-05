#!/usr/bin/python
from datetime import datetime

from flask_login import UserMixin
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
ma = Marshmallow()


class User(db.Model, UserMixin):
    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # LastFM settings
    fm_name = db.Column(db.String(), nullable=True, default='')
    fm_sk = db.Column(db.String(32), nullable=True, default='')

    def setpass(self, password):
        self.password = generate_password_hash(password)

    def checkpass(self, password):
        return check_password_hash(self.password, password)

    def lastfm_connected(self):
        if self.fm_sk != '':
            return True
        return False

    def __repr__(self):
        return '<User %r>' % self.name


class Video(db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(25), unique=False,
                          nullable=False)  # YouTube watch ID
    title = db.Column(db.String(100), unique=False, nullable=False)
    # TODO: specify resolution
    thumbnail = db.Column(db.String, unique=False, nullable=False)
    room = db.relationship('Room', backref='video', lazy=True)
    date = db.Column(db.DateTime, default=datetime.now())  # Date watched
    user = db.relationship('User', backref='video', lazy=True)

    def __repr__(self):
        return '<Video: %r, %r>' % (self.unique_id, self.title)


# Allows room video history to be serialized to JSON
class HistorySchema(ma.ModelSchema):
    class Meta:
        model = Video
        # fields = ('pk', 'player', 'unique_id', 'title', 'thumbnail', 'twitch_avatar', 'date')


# many to many relationship btwn user & room
users = db.Table('users',
                 db.Column('room_id', db.Integer, db.ForeignKey(
                     'room.pk'), primary_key=True),
                 db.Column('user_id', db.Integer, db.ForeignKey(
                     'user.pk'), primary_key=True)
                 )


class Room(db.Model):
    pk = db.Column(db.Integer, primary_key=True)

    # use Room.query.with_parent(user_object) to get user's rooms
    # use Room.users to get users in room
    users = db.relationship(
        'User', secondary=users, lazy='subquery', backref=db.backref('rooms', lazy=True))

    # TODO: fix
    def get_online_users(self):
        """
        active_users = []

        # Retrieve server:logged from cache
        logged_in = pipe.lrange('server:logged', 0, -1).execute()[0]
        # Decode byte string from redis to Python string
        logged_in = [user.decode('utf-8') for user in logged_in]
        # Generate list of online/offline users
        #   1 => Online
        #   2 => Offline
        for user in models.User.query.all():
            if user.username in logged_in:
                active_users.append((user.username, 1))
            else:
                active_users.append((user.username, 0))
        """
        return []

    # Retrieve most recent object from history
    def get_most_recent_video(self):
        schema = HistorySchema()
        video = Video.query.order_by(db.text('-pk')).first()

        return schema.dump(video)

    # Retrieve last 20 objects from history
    def get_recent_history(self):
        schema = HistorySchema(many=True)
        videos = Video.query.order_by(db.text('-pk')).limit(20).all()

        return schema.dump(videos)

    def __repr__(self):
        return '<Room: %r, %r>' % (self.pk, self.unique_id)