from flask import Flask

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/echo/<thing>')
def echo(thing):
    return 'Say hello to {0}'.format(thing)

@app.route('/api/gettickerlist')
def gettickerlist():
    import os
    l = os.listdir(path='../data')
    return {'data': l}

app.run(port=9999, debug=True)