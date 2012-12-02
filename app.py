import os
from flask import Flask
from flask import Response
from flask import render_template
from flask import abort
from flask import request
import redis
from json import loads

app = Flask(__name__)
r = redis.from_url(os.environ['REDISTOGO_URL'])


@app.route('/')
def index():
    items = r.get('index')
    last_update = r.get('last_update')
    return render_template('index.html', host=request.headers.get('Host'), items=loads(items), last_update=last_update)

@app.route('/<cat_id>.rss')
def rss(cat_id):
    ret = r.get('%s.rss' % cat_id)
    if ret:
        return Response(ret, mimetype='application/rss+xml')
    else:
        abort(404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)