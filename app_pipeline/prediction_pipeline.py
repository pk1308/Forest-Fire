from app_logger.logger import App_Logger
from app_exception.exception import AppException
import pandas as pd 
import sys
import os
from app_util.util import load_object


prediction = App_Logger(__name__)

class PredictionPipeline:
    
    def __init__(self, model_dir : str , columns_transformer_dir : str):
        try :
            self.model_dir = model_dir
            self.columns_transformer_dir = columns_transformer_dir
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
    def predict(self, X):
        try:
            model_path = self.get_latest_model_path()
            model = load_object(file_path=model_path)
            columns_transformer_path = self.get_latest_columns_transformer_path()
            columns_transformer = load_object(file_path=columns_transformer_path)
            X[X.columns] = columns_transformer.transform(X[X.columns])
            y_pred = model.predict(X)
            response = pd.DataFrame(y_pred, columns=['prediction']).applymap(lambda x: "Fire" if x == 1 else "No Fire")
            return response
        except Exception as e:
            raise AppException(e, sys) from e
    

