# from app_pipeline.prediction_pipeline import PredictionPipeline
# from app_config.constants import *
# from app_util.util import read_yaml_file
from flask import Flask, request
from flask import send_file, abort, render_template ,request, jsonify
from wsgiref import simple_server
from flask import Flask, request, render_template
from flask import Response
from flask_cors import CORS, cross_origin
import os
import pandas as pd 


# config_info = read_yaml_file(file_path=CONFIG_FILE_PATH )
# model_pusher_config = config_info[MODEL_PUSHER_CONFIG_KEY]
# data_validation_config = config_info[DATA_VALIDATION_CONFIG_KEY]
# validation_config_dir = data_validation_config[DATA_VALIDATION_CONFIG_DIR]
# model_dir = os.path.join(ROOT_DIR, model_pusher_config[MODEL_PUSHER_MODEL_EXPORT_DIR_KEY])
# schema_file_path = os.path.join(
#     ROOT_DIR, validation_config_dir, data_validation_config[DATA_VALIDATION_SCHEMA_FILE_NAME_KEY])
# columns_transformer_dir = os.path.join(ROOT_DIR , model_pusher_config[PREPROCESSING_EXPORT_DIR_KEY])
# prediction_pipeline_obj = PredictionPipeline(model_dir=model_dir,\
#                                         columns_transformer_dir=columns_transformer_dir,\
#                                         schema_file_path=schema_file_path)

app = Flask(__name__) # create the Flask app



CORS(app)

@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({'status': str(e)})

@app.route('/eda', methods=['POST', 'GET'])
@cross_origin()
def eda():
    try:
        return render_template('eda.html')
    except Exception as e:
        return jsonify({'status': str(e)})

@app.route('/uploader',methods=['POST', 'GET'])
@cross_origin()
def predictfile():

    try:
        if request.method == 'POST':
            file = request.files['file']
            if file is not None:
               
                df = pd.read_csv(file)
                print(df)

                prediction = prediction_pipeline_obj.predict(df)
                print(prediction)
                return send_file(prediction, as_attachment=True)
            else:
                return Response(status=400)
    except Exception as e:
        return str(e)
        
@app.route('/predict', methods=['POST', 'GET'])
@cross_origin()
def predict():
    try:
        if request.method == 'POST':
            data = request.form.to_dict()
            df = pd.DataFrame(data , index = [0])
            print(df)
            prediction = prediction_pipeline_obj.predict(df)
            
            return send_file(prediction, as_attachment=True)
            
    except Exception as e:
        return str(e)


if __name__=="__main__":
    app.run()





