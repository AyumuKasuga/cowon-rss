import os
from flask import Flask
import redis

app = Flask(__name__)
r = redis.from_url(os.environ['REDISTOGO_URL'])


@app.route('/')
def index():
    return r.get('index.html', 'None')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)