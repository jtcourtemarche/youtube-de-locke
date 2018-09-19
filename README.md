![alt text](https://github.com/jtcourtemarche/youtube-de-locke/blob/master/static/images/logo.png "youtube de locke")

Website built on Flask that synchronizes Youtube videos using websockets.

```
# You must create an api.py file with variables 
# 	API_KEY -> Youtube API key
#	SECRET_KEY -> Secret key for Flask

# Setup
pip install -r requirements.txt 

python 
>> import manage
>> manage.init_db()
>> manage.add_user('username', 'password')
>> exit()

# Run locally
flask run

# Run w/ gunicorn 
gunicorn app:app --bind 0.0.0.0:5000 --reload -k "geventwebsocket.gunicorn.workers.GeventWebSocketWorker" 
```