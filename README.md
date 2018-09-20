<p align="center">
  <img src="https://github.com/jtcourtemarche/youtube-de-locke/blob/master/static/images/logo.png" alt="youtube-de-locke" width="539" />
</p>

Platform built on Flask that synchronizes Youtube videos using websockets.

This application requires that you to have a PostgreSQL server already set up.
Put your credentials in the api.py file.

```python
# Example postgres import

POSTGRES = {
    'user': 'postgres',
    'pw': 'password',
    'db': 'mydatabase',
    'host': 'localhost',
    'port': '5432',
}
```

All of your API keys belong in the api.py file as well.
Your api.py file setup should look similar to this:

```python
API_KEY = "<youtube api key>"
SECRET_KEY = "<secret key for flask>"

# If you want LastFM integration (these are optional)
LASTFM_KEY = "<lastfm api key>"
LASTFM_SECRET = "<lastfm secret key>"
```
Python setup is as follows:

```python
$ pip install -r requirements.txt 

$ python 
>> import manage
>> manage.init_db()
>> manage.add_user('<username>', '<password>')
>> exit()

# Run locally
$ flask run

# Or run w/ Gunicorn 
$ gunicorn app:app --bind 0.0.0.0:5000 --reload -k "geventwebsocket.gunicorn.workers.GeventWebSocketWorker" 
```
