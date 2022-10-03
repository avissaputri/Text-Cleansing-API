#import library
import re
import sqlite3
import pandas as pd
import csv
from flask import Flask, request, jsonify, make_response
from flask_swagger_ui import get_swaggerui_blueprint

#function initiation
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

#database installation
data_base = sqlite3.connect('data.db', check_same_thread=False)

#row factory
#create row in table
data_base.row_factory = sqlite3.Row

#define cursor
mycursor = data_base.cursor()
#create table in database
data_base.execute('''CREATE TABLE IF NOT EXISTS data (old_text varchar(255), text_clean varchar(255));''')

#route swagger url
#UI display
SWAGGER_URL = '/docs'
#UI respond in static
API_URL             = '/static/docs.json'
SWAGGERUI_BLUEPIRNT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name'  : "TeClean"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPIRNT, url_prefix=SWAGGER_URL)

#route to clean inputed text methods=["POST"]
@app.route("/data", methods=['POST'])
def data():
    #get text file
    text       = str(request.form["text"])
    #cleansing process
    text_clean = re.sub(r'[^a-zA-Z0-9]', ' ', text)

    #input data to database
    query_text = "insert into data(old_text, text_clean) values (?,?)"

    #save inputted data
    val = (text, text_clean)
    
    mycursor.execute(query_text, val)
    data_base.commit()
    
    return text_clean

#route to upload csv and clean csv data 
@app.route("/data/csv", methods=["POST"])
def input_csv():
    #upload file
    if request.method == "POST":
        file = request.files['file']
        try:
            data = pd.read_csv(file, encoding='iso-8859-1')
        except:
            data = pd.read_csv(file, encoding='utf-8')
        (data)

        #file_clean = ""

        for line in str(data):
            #file_clean = file_clean + re.sub(r'[^a-zA-Z0-9]', ' ', str(data))
            file_clean = re.sub(r'[^a-zA-Z]', ' ', str(data))
        
        #input data to database
        query_text = "insert into data(old_text, text_clean) values (?,?)"

        #save inputted data
        val = (str(data), file_clean)
    
        mycursor.execute(query_text, val)
        data_base.commit()
        
        return file_clean

#error handling
@app.errorhandler(400)
def handle_400_error(_error):
  "return a http 400 error to client"
  return make_response(jsonify({'error':'Misunderstood'}), 400)

@app.errorhandler(401)
def handle_401_error(_error):
  "return a http 401 error to client"
  return make_response(jsonify({'error':'Unauthorised'}), 401)

@app.errorhandler(404)
def handle_404_error(_error):
  "return a http 404 error to client"
  return make_response(jsonify({'error':'Not Found'}), 404)

@app.errorhandler(500)
def handle_500_error(_error):
  "return a http 500 error to client"
  return make_response(jsonify({'error':'Server Error'}), 500)

if __name__ == '__main__':
  app.run(debug=True)
