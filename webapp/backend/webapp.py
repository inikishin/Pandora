import os
import logging
import json
from flask import Flask
from flask_cors import CORS, cross_origin
from tasks import processloadquotes, check_status

FORMAT = '%(asctime)-15s %(module)s %(message)s'
logging.basicConfig(filename='../../logs/main.log', level=logging.INFO, format=FORMAT)
extra_info_logging = {'module': __name__}
#logging.info('Module started...', extra=extra_info_logging)

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/loadquotes')
@cross_origin()
def loadquotes():
    #logging.info('Call loadquotes()', extra=extra_info_logging)
    ar = processloadquotes.delay(['GAZP', 'SBER', 'NVTK', 'FIVE', 'ALRS'])
    return json.dumps({'id': ar.id})

@app.route('/api/preprocessing')
def preprocessing():
    #logging.info('Call preprocessing()', extra=extra_info_logging)
    return 'id'

@app.route('/api/getaskstatus/<id>')
@cross_origin()
def getaskstatus(id):
    r = check_status(id)
    return json.dumps(r)

@app.route('/api/gettickerlist')
def gettickerlist():
    import os
    l = os.listdir(path='../data')
    return {'data': l}

app.run(port=9999, debug=True)