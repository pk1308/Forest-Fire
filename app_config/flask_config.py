import sys
from app_config.constants import *
from app_util.util import read_yaml_file
from app_exception.exception import AppException
from app_entity.config_entity import FlaskConfig
from app_pipeline.prediction_pipeline import PredictionPipeline

class FlaskAppConfiguration:
    def __init__(self, config_file_path: str = CONFIG_FILE_PATH, current_time_stamp: str = CURRENT_TIME_STAMP):
        """
        Initializes the AppConfiguration class.
        config_file_path: str
        By default it will accept default config file path.
        """
        try:
            self.config_info = read_yaml_file(file_path=config_file_path)
            self.time_stamp = current_time_stamp
        except Exception as e:
            raise AppException(e, sys) from e
    def get_flask_config(self) -> str:
        try:
            model_pusher_config = self.config_info[MODEL_PUSHER_CONFIG_KEY]
            data_validation_config = self.config_info[DATA_VALIDATION_CONFIG_KEY]
            validation_config_dir = data_validation_config[DATA_VALIDATION_CONFIG_DIR]
            model_dir = os.path.join(ROOT_DIR, model_pusher_config[MODEL_PUSHER_MODEL_EXPORT_DIR_KEY])
            schema_file_path = os.path.join(
                ROOT_DIR, validation_config_dir, data_validation_config[DATA_VALIDATION_SCHEMA_FILE_NAME_KEY])
            columns_transformer_dir = os.path.join(ROOT_DIR , model_pusher_config[PREPROCESSING_EXPORT_DIR_KEY])
            prediction_pipeline = PredictionPipeline(model_dir=model_dir,\
                                                    columns_transformer_dir=columns_transformer_dir,\
                                                    schema_file_path=schema_file_path)
            response = FlaskConfig(prediction_pipeline_obj=prediction_pipeline , 
                                    schema_file_path = schema_file_path )              
            return response
        except Exception as e:
            raise AppException(e, sys) from e