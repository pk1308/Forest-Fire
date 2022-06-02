from app_config.configuration import AppConfiguration
from app_exception.exception import AppException
from app_entity.config_entity import FlaskConfig
from flask import Flask, request
from flask import send_file, abort, render_template
import os


AppConfiguration = AppConfiguration()
prediction_config = AppConfiguration.get_flask_config()

app = Flask(__name__) # create the Flask app

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return str(e)

@app.route('/eda', methods=['POST'])
def eda():
    try:
        return render_template('eda.html')
    except Exception as e:
        return str(e)

if __name__=="__main__":
    app.run(debug=True)






