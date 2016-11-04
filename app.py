__author__ = 'Josh Firminger'

#import flask
from flask import Flask, request, jsonify, url_for, render_template
import pandas as pd
from sklearn.externals import joblib

model_directory = 'model'
model_file_name = '%s/model.pkl' % model_directory
model_columns_file_name = '%s/model_columns.pkl' % model_directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except Exception, e:
        port = 8080

    try:
        clf = joblib.load(model_file_name)
        print 'model loaded'
        model_columns = joblib.load(model_columns_file_name)
        print 'model columns loaded'

    except Exception, e:
        print('No Model')

    app.run(port=port, debug=True)
