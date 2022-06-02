
from datetime import datetime
import os
import sys


from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier

from app_logger.logger import App_Logger
from app_exception.exception import AppException
from app_entity.config_entity import DataIngestionConfig, DataValidationConfig, DataTransformationConfig, \
    ModelTrainerConfig, ModelEvaluationConfig
from app_entity.config_entity import ModelPusherConfig, TrainingPipelineConfig
from app_util.util import read_yaml_file
from app_database.mongoDB import MongoDB
from app_config.constants import *

config_log = App_Logger("configuration")


class AppConfiguration:
    def __init__(self, config_file_path: str = CONFIG_FILE_PATH, current_time_stamp: str = CURRENT_TIME_STAMP):
        """
        Initializes the AppConfiguration class.
        config_file_path: str
        By default it will accept default config file path.
        """
        try:
            self.config_info = read_yaml_file(file_path=config_file_path)
            self.training_pipeline_config = self.get_training_pipeline_config()
            self.time_stamp = current_time_stamp
        except Exception as e:
            raise AppException(e, sys) from e

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        try:
            artifact_dir = self.training_pipeline_config.artifact_dir
            data_ingestion_config = self.config_info[DATA_INGESTION_CONFIG_KEY]
            raw_data_dir = os.path.join(
                artifact_dir, data_ingestion_config[DATA_INGESTION_RAW_DATA_DIR_KEY])
            ingested_dir_name = os.path.join(artifact_dir,
                                             data_ingestion_config[DATA_INGESTION_DIR_NAME_KEY])

            ingested_train_dir = os.path.join(ingested_dir_name,
                                              data_ingestion_config[DATA_INGESTION_TRAIN_DIR_KEY])

            ingested_test_dir = os.path.join(ingested_dir_name,
                                             data_ingestion_config[DATA_INGESTION_TEST_DIR_KEY])
            ingested_raw_collection = MongoDB(collection_name=data_ingestion_config[DATA_INGESTION_COLLECTION], \
                                              drop_collection=True)
            ingested_train_collection = MongoDB(collection_name=data_ingestion_config[DATA_INGESTION_TRAIN_COLLECTION],
                                                drop_collection=True)
            ingested_test_collection = MongoDB(collection_name=data_ingestion_config[DATA_INGESTION_TEST_COLLECTION],
                                               drop_collection=True)

            response = DataIngestionConfig(dataset_download_url=data_ingestion_config[DATA_INGESTION_DOWNLOAD_URL_KEY],
                                           raw_data_dir=raw_data_dir,
                                           ingested_train_dir=ingested_train_dir,
                                           ingested_test_dir=ingested_test_dir,
                                           raw_data_collection=ingested_raw_collection,
                                           ingested_train_collection=ingested_train_collection,
                                           ingested_test_collection=ingested_test_collection)

            config_log.info(f"Data Ingestion Config: {response}")

            return response
        except Exception as e:
            raise AppException(e, sys) from e

    def get_data_validation_config(self) -> DataValidationConfig:
        try:
            data_ingestion_config = self.config_info[DATA_INGESTION_CONFIG_KEY]
            data_validation_config = self.config_info[DATA_VALIDATION_CONFIG_KEY]
            validation_config_dir = data_validation_config[DATA_VALIDATION_CONFIG_DIR]
            schema_file_path = os.path.join(
                ROOT_DIR, validation_config_dir, data_validation_config[DATA_VALIDATION_SCHEMA_FILE_NAME_KEY])
            ingested_train_collection = MongoDB(collection_name=data_ingestion_config[DATA_INGESTION_TRAIN_COLLECTION], \
                                                drop_collection=False)
            ingested_test_collection = MongoDB(collection_name=data_ingestion_config[DATA_INGESTION_TEST_COLLECTION], \
                                               drop_collection=False)

            response = DataValidationConfig(schema_file_path=schema_file_path,
                                            Train_collection=ingested_train_collection,
                                            Test_collection=ingested_test_collection)
            config_log.info(response)
            return response
        except Exception as e:
            raise AppException(e, sys) from e

    def get_data_transformation_config(self) -> DataTransformationConfig:

        try:
            data_transformation_config = self.config_info[DATA_TRANSFORMATION_CONFIG_KEY]
            artifact_dir = os.path.join(
                self.training_pipeline_config.artifact_dir, DATA_TRANSFORMATION_ARTIFACT_DIR, self.time_stamp)

            data_transformation_config = self.config_info[DATA_TRANSFORMATION_CONFIG_KEY]
            transformed_dir = os.path.join(
                artifact_dir, data_transformation_config[DATA_TRANSFORMATION_DIR_NAME_KEY])
            transformed_train_dir = os.path.join(
                transformed_dir, data_transformation_config[DATA_TRANSFORMATION_TRAIN_DIR_NAME_KEY])
            transformed_test_dir = os.path.join(
                transformed_dir, data_transformation_config[DATA_TRANSFORMATION_TEST_DIR_NAME_KEY])

            preprocessing_dir = os.path.join(
                artifact_dir, data_transformation_config[DATA_TRANSFORMATION_PREPROCESSING_DIR_KEY])

            preprocessed_file_name = data_transformation_config[
                DATA_TRANSFORMATION_PREPROCESSED_FILE_NAME_KEY]

            preprocessed_object_file_path = os.path.join(preprocessing_dir, preprocessed_file_name)
            processed_train_collection = MongoDB(
                collection_name=data_transformation_config[PROCESSED_TRAIN_COLLECTION_KEY], \
                drop_collection=True)
            processed_test_collection = MongoDB(
                collection_name=data_transformation_config[PROCESSED_TEST_COLLECTION_KEY], \
                drop_collection=True)

            response = DataTransformationConfig(transformed_test_dir=transformed_test_dir,
                                                transformed_train_dir=transformed_train_dir,
                                                preprocessed_object_file_path=preprocessed_object_file_path,
                                                processed_train_collection=processed_train_collection,
                                                processed_test_collection=processed_test_collection)

            config_log.info(f"Data Transformation Config: {response}")
            return response
        except Exception as e:
            raise AppException(e, sys) from e

    def get_model_trainer_config(self) -> ModelTrainerConfig:
        try:
            model_trainer_config = self.config_info[MODEL_TRAINER_CONFIG_KEY]
            data_transformation_config = self.config_info[DATA_TRANSFORMATION_CONFIG_KEY]
            artifact_dir = os.path.join(self.training_pipeline_config.artifact_dir,
                                        MODEL_TRAINER_ARTIFACT_DIR,
                                        self.time_stamp)

            model_dir = os.path.join(artifact_dir, model_trainer_config[MODEL_TRAINER_DIR_KEY])
            model_file_path = os.path.join(model_dir, model_trainer_config[MODEL_TRAINER_FILE_NAME_KEY])

            base_accuracy = model_trainer_config[MODEL_TRAINER_BASE_ACCURACY_KEY]
            
            train_collection = MongoDB(collection_name=data_transformation_config[PROCESSED_TRAIN_COLLECTION_KEY], \
                                                drop_collection=False)
            test_collection = MongoDB(collection_name=data_transformation_config[PROCESSED_TEST_COLLECTION_KEY], \
                                                  drop_collection=False)    
            randomforest_params =  model_trainer_config[RANDOMFOREST_PARAMS_CONFIG_KEY]
            randomforest = RandomForestClassifier(**randomforest_params )
            svc_params =  model_trainer_config [SVC_PARAMS_CONFIG_KEY]
            svc = SVC(**svc_params)
            gradientboosting_params =  model_trainer_config[GRADIENT_BOOSTING_PARAMS_CONFIG_KEY]
            gradientboosting = GradientBoostingClassifier(**gradientboosting_params)

            model_list = [randomforest, svc, gradientboosting]

            response = ModelTrainerConfig(trained_model_file_path= model_file_path,
                                        train_collection = train_collection,
                                        test_collection = test_collection,
                                        base_accuracy=base_accuracy,
                                        model_list = model_list)

            config_log.info(f"Model Trainer Config: {response}")
            return response
        except Exception as e:
            raise AppException(e, sys) from e

    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        try:
            model_evaluation_config = self.config_info[MODEL_EVALUATION_CONFIG_KEY]
            artifact_dir = os.path.join(self.training_pipeline_config.artifact_dir,
                                        MODEL_EVALUATION_ARTIFACT_DIR, )

            model_evaluation_file_path = os.path.join(artifact_dir,
                                                      model_evaluation_config[MODEL_EVALUATION_FILE_NAME_KEY])
            response = ModelEvaluationConfig(model_evaluation_file_path=model_evaluation_file_path,
                                             time_stamp=self.time_stamp)

            config_log.info(f"Model Evaluation Config: {response}.")
            return response
        except Exception as e:
            raise AppException(e, sys) from e

    def get_model_pusher_config(self) -> ModelPusherConfig:
        try:
            time_stamp = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
            model_pusher_config = self.config_info[MODEL_PUSHER_CONFIG_KEY]
            export_dir_path = os.path.join(ROOT_DIR, model_pusher_config[MODEL_PUSHER_MODEL_EXPORT_DIR_KEY],
                                           time_stamp)

            response = ModelPusherConfig(export_dir_path=export_dir_path)
            config_log.info(f"Model pusher config {response}")
            return response
        except Exception as e:
            raise AppException(e, sys) from e

    def get_training_pipeline_config(self) -> TrainingPipelineConfig:
        try:
            training_pipeline_config = self.config_info[TRAINING_PIPELINE_CONFIG_KEY]
            artifact_dir = os.path.join(
                ROOT_DIR,training_pipeline_config[TRAINING_PIPELINE_ARTIFACT_DIR_KEY])
            response = TrainingPipelineConfig(artifact_dir=artifact_dir)
            config_log.info(f"Training Pipeline Config: {response}")
            return response
        except Exception as e:
            raise AppException(e, sys) from e

    def get_housing_prediction_model_dir(self) -> str:
        try:
            model_pusher_config = self.config_info[MODEL_PUSHER_CONFIG_KEY]
            return os.path.join(ROOT_DIR, model_pusher_config[MODEL_PUSHER_MODEL_EXPORT_DIR_KEY])
        except Exception as e:
            raise AppException(e, sys) from e


if __name__ == '__main__':
    try:
        app_config = AppConfiguration()
        print(app_config.get_data_ingestion_config())
    except Exception as e:
        print(e)
