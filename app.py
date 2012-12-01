import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    root_path = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.abspath(os.path.join(root_path, 'static'))
    return open(static_path + '/index.html', 'r').read()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)