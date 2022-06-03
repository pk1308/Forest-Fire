# doing necessary imports

import threading
import io
import time
from flask import Flask, render_template, request, jsonify, Response, url_for, redirect
from flask_cors import CORS, cross_origin


master_db_name = "check1223"


# To avoid the time out issue on heroku
class threadClass:

    def __init__(self ):
        global master_db_name
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution
    
    def run(self):
        global master_db_name
        scrapper = Run(db_name=master_db_name)
        logging.info("Thread run completed")
        logging.debug(scrapper)




app = Flask(__name__)  # initialising the flask app with the name 'app'

@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def index():
    return render_template('index.html')

@app.route('/test', methods=['POST', 'GET'])
@cross_origin()
def index1():

    mongodb_master_collection = MongoDB(db_name, 'Final')
    master_data_course = set() 
    master_data_response = []
    
    if request.method == 'POST':
        Selected_attribute = request.form.get('attribute')
        Selected_Category = request.form['category']
        Selected_Course = request.form['course']
        if Selected_Course is None:
            logging.info(f'No Course Selected  Selected category {Selected_Category}')
            master_data = mongodb_master_collection.find_many({'category' : Selected_Category})
            for data in master_data:
                master_data_course.add(data['course_name'])
                logging.info(f'course Retrived for category {Selected_Category}')
                
            return render_template('index.html', course_attributes = Selected_attribute ,
                               course_category = Selected_Category, course_coursename = master_data_course)
        else:
            master_data_response = mongodb_master_collection.find_one({'course_name' : Selected_Course})
            logging.info(f'Course Selected {Selected_Course} selected category {Selected_Category} attribute {Selected_attribute}')
            response_data = master_data_response["Selected_attribute"]
            return Response(response=response_data, status=200)

    else:
        master_data = mongodb_master_collection.find_many()
        master_data_attribute = ['description', 'price', 'course_features', 'what_youll_learn', 'timings',
                    'requirements', 'course_curriculum_dict', 'mentor_names', 'category', 'course_link']
        master_data_category = [data['category'] for data in master_data]
        logging.info(f'Master Data Category {master_data_category}')
        return render_template('index.html' , course_attributes = master_data_attribute ,
                               course_category = master_data_category )


@app.route('/scrap', methods=['GET' , 'POST'])
@cross_origin()
def scrap():

    threadClass()
    # Run(db_name=master_db_name)
    return jsonify({'status': 'OK'})

if __name__ == "__main__":
    app.run()  # running the app on the local machine on port 8000