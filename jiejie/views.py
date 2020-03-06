#!/usr/bin/python
from flask import Blueprint
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

import jiejie.models as models
from config import LASTFM_KEY
from extensions import fm
from extensions import login_manager
from extensions import pipe

# Register these views with app
urls = Blueprint('urls', __name__)

# Login manager user handler
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

# Make current_user a global variable
@urls.before_request
def before_request():
    g.user = current_user

# Index page
@urls.route('/')
def root():
    if g.user.is_authenticated:
        return render_template(
            'lobby.html',
            rooms=models.Room.query.with_parent(g.user)
        )

    return render_template('login.html')


@urls.route('/create/room', methods=['POST'])
@login_required
def create_room():
    if request.form:
        # TODO: use Flask-WTF forms for this
        room = models.Room(
            name=request.form['room_name']
        )

        models.db.session.add(room)
        models.db.session.commit()

        g.user.join_room(room)

    return redirect('/')

# Standard viewing page
@urls.route('/watch/<int:room_id>')
@login_required
def room(room_id):
    room = models.Room.query.filter_by().first()

    if room:
        if room.public or g.user in room.users:
            return render_template('index.html')

    return 'Room doesn\'t exist.'

# User history
@urls.route('/~<string:name>/history/<int:index>')
@urls.route('/~<string:name>/history')
@login_required
def user_history(name, index=1):
    user = models.User.query.filter_by(name=name).first()
    if user:
        return render_template(
            'history.html',
            history=user.videos[25*(index-1):25*index]
        )
    else:
        return 'User ' + name + ' does not exist.'

# User profiles
@urls.route('/~<string:name>')
@login_required
def user_profile(name):
    user = models.User.query.filter_by(name=name).first()
    if user:
        if user.lastfm_connected():
            lastfm_data = fm.get_user(user.fm_name)
        else:
            lastfm_data = None

        # get most played video
        most_played = None
        if user.videos:
            video_watch_ids = [v.watch_id for v in user.videos]
            most_played = max(set(video_watch_ids), key=video_watch_ids.count)
            most_played = models.Video.query.filter_by(
                watch_id=most_played).first()

        return render_template(
            'profile.html',
            user=user,
            total_plays=len(user.videos),
            most_played=most_played,
            lastfm=lastfm_data
        )

    return 'User ' + name + ' does not exist.'

# Login view
@urls.route('/login', methods=['POST'])
def login():
    # Retrieve server:logged from cache
    logged_in = pipe.lrange('server:logged', 0, -1).execute()[0]
    # Decode byte string from redis to Python string
    logged_in = [user.decode('utf-8') for user in logged_in]

    if g.user.is_authenticated:
        return redirect('/watch')
    else:
        username = models.User.query.filter_by(
            name=request.form['username']).first()
        if username:
            if username.checkpass(request.form['password']):
                login_user(username)
                return redirect('/watch')
            else:
                return render_template('login.html', error='Invalid password')
        else:
            return render_template('login.html', error='Invalid username')


# Logout view
@urls.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


# Redirect user to LastFM authentication page
@urls.route('/auth/lastfm')
@login_required
def auth_lastfm():
    if not current_user.lastfm_connected():
        return redirect(f'http://www.last.fm/api/auth/?api_key={LASTFM_KEY}')

    return f'Your account {current_user.fm_name} is already connected'


# Register LastFM credentials into ytdl database
@urls.route('/register', methods=['GET'])
@login_required
def register():
    if 'token' in request.args and len(request.args['token']) == 32:
        token = request.args['token']

        resp = fm.get_session(token)

        if resp[0]:
            # Register LastFM in DB
            current_user.fm_name = resp[1]['name']
            current_user.fm_token = token
            current_user.fm_sk = resp[1]['key']

            models.db.session.commit()

            return '<span>Registered {}</span><br/><a href="/">Take me back</a>'.format(resp[1]['name'])
        else:
            return 'Error connecting to your LastFM account: {}'.format(resp[1]['message'])
    else:
        return 'Failed to connect to your LastFM'


# Page errors


@urls.errorhandler(404)
def page_not_found(error):
    return redirect('/')


@urls.errorhandler(401)
def unauthorized(error):
    return redirect('/')
