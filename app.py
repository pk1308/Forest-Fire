from app_config.configuration import AppConfiguration
from app_exception.exception import AppException
from app_entity.config_entity import FlaskConfig
from flask import Flask, request
from flask import send_file, abort, render_template ,request, jsonify
from wsgiref import simple_server
from flask import Flask, request, render_template
from flask import Response
from flask_cors import CORS, cross_origin
import os
import pandas as pd 


AppConfiguration = AppConfiguration()
prediction_config = AppConfiguration.get_flask_config()

app = Flask(__name__) # create the Flask app



CORS(app)

@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return str(e)

@app.route('/eda', methods=['POST'])
@cross_origin()
def eda():
    try:
        return render_template('eda.html')
    except Exception as e:
        return str(e)

@app.route('/uploader', methods=['POST'])
def predictfile():
    try:
        if request.method == 'POST':
            file = request.files['file']
            if file is not None:
               
                df = pd.read_csv(file)
                print(df)

                prediction = prediction_config.prediction_pipeline_obj.predict(df)
                print(prediction)
                return send_file(prediction, as_attachment=True)
            else:
                return Response(status=400)
    except Exception as e:
        return str(e)
        
@app.route('/predict', methods=['POST'])
def predict():
    try:
        if request.method == 'POST':
            data = request.form.to_dict()
            df = pd.DataFrame(data , index = [0])
            print(df)
            prediction = prediction_config.prediction_pipeline_obj.predict(df)
            
            return send_file(prediction, as_attachment=True)
            
    except Exception as e:
        return str(e)


port = int(os.getenv("PORT", 5000))
if __name__=="__main__":
    app.run()





