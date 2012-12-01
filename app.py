import os
from flask import Flask
from flask import Response
import redis

app = Flask(__name__)
r = redis.from_url(os.environ['REDISTOGO_URL'])


@app.route('/')
def index():
    ret = r.get('index.html')
    return ret if ret else 'None'

@app.route('/<cat_id>.rss')
def rss(cat_id):
    ret = r.get('%s.rss' % cat_id)
    if ret:
        return Response(ret, mimetype='application/rss+xml')
    else:
        return 'None'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)