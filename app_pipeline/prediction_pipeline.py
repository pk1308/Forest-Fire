
from copy import copy
from numpy import NaN
import pandas as pd 
import sys
import os
from app_util.util import load_object , read_yaml_file
from app_logger.logger import App_Logger
from app_exception.exception import AppException
from app_config.constants import *


prediction = App_Logger(__name__)

class PredictionPipeline:
    
    def __init__(self, model_dir : str , columns_transformer_dir : str , schema_file_path : str):
        try :
            self.model_dir = model_dir
            self.columns_transformer_dir = columns_transformer_dir
            self.scheme_path = schema_file_path
            self.prediction_path = os.path.join(ROOT_DIR, 'prediction')
        except Exception as e:
            prediction.error(e)
            raise AppException(e, sys) from e

    def get_latest_model_path(self):
        try:
            folder_name = list(map(int, os.listdir(self.model_dir)))
            latest_model_dir = os.path.join(self.model_dir, f"{max(folder_name)}")
            file_name = os.listdir(latest_model_dir)[0]
            latest_model_path = os.path.join(latest_model_dir, file_name)
            return latest_model_path
        except Exception as e:
            raise AppException(e, sys) from e
    
    def get_latest_columns_transformer_path(self):
        try:
            folder_name = list(map(int, os.listdir(self.columns_transformer_dir)))
            latest_columns_transformer_dir = os.path.join(self.columns_transformer_dir, f"{max(folder_name)}")
            file_name = os.listdir(latest_columns_transformer_dir)[0]
            latest_columns_transformer_path = os.path.join(latest_columns_transformer_dir, file_name)
            return latest_columns_transformer_path
        except Exception as e:
            raise AppException(e, sys) from e
    def predict(self,Predict_df : pd.DataFrame):
        try:
            model_path = self.get_latest_model_path()
            model = load_object(file_path=model_path)
            dataset_schema = read_yaml_file(self.scheme_path)
            scheme_dict = dataset_schema[DATASET_SCHEMA_COLUMNS_KEY]
            Predict_df.fillna(value=NaN, inplace=True)
            
            for key , value in scheme_dict.items():
                Predict_df[key] = Predict_df[key].astype(value)
            
            

            # splitting input columns and target column
            # TARGET_COLUMN
            target_column = dataset_schema[DATASET_SCHEMA_TARGET_COLUMN_KEY]

            # dropping categorical columns selecting only numerical columns to replace missing
            # value of numerical column
            columns = list(dataset_schema[DATASET_SCHEMA_COLUMNS_KEY].keys())
            
            columns.remove(target_column)
            X = Predict_df[columns].copy()
        
             
            y = Predict_df[target_column]
            columns_transformer_path = self.get_latest_columns_transformer_path()
            columns_transformer = load_object(file_path=columns_transformer_path)
            X[X.columns] = columns_transformer.transform(X[X.columns])
            y_pred = model.predict(X)
            prediction = pd.DataFrame(y_pred, columns=['prediction']).applymap(lambda x: "Fire" if x == 1 else "No Fire")
            prediction_file = pd.concat([Predict_df, prediction], axis=1)
            prediction_filename = os.path.join(self.prediction_path, 'prediction.csv')
            os.makedirs(self.prediction_path, exist_ok=True)
            prediction_file.to_csv(prediction_filename, index=False)
            response = prediction_filename


            return response
        except Exception as e:
            raise AppException(e, sys) from e
    

