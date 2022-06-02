from app_exception.exception import AppException
from collections import namedtuple

DataIngestionConfig = namedtuple("DatasetConfig", ["dataset_download_url",
                                                   "raw_data_dir",
                                                   "ingested_train_dir",
                                                   "ingested_test_dir",
                                                   "raw_data_collection",
                                                   "ingested_train_collection",
                                                   "ingested_test_collection"])

DataValidationConfig = namedtuple("DataValidationConfig", ["schema_file_path",
                                                           "Train_collection",
                                                           "Test_collection"])

DataTransformationConfig = namedtuple("DataTransformationConfig", ["transformed_train_dir",
                                                                   "transformed_test_dir",
                                                                   "preprocessed_object_file_path",
                                                                   "processed_train_collection",
                                                                   "processed_test_collection"])

ModelTrainerConfig = namedtuple("ModelTrainerConfig", ["trained_model_file_path",
                                                       "train_collection",
                                                       'test_collection',
                                                       "base_accuracy",
                                                       "model_list"])

ModelEvaluationConfig = namedtuple("ModelEvaluationConfig", ["model_evaluation_file_path", "time_stamp"])

ModelPusherConfig = namedtuple("ModelPusherConfig", ["model_export_dir_path", "preprocessing_export_dir_path"])

TrainingPipelineConfig = namedtuple("TrainingPipelineConfig", ["artifact_dir"])

FlaskConfig = namedtuple("FlaskConfig", ["prediction_pipeline_obj" , "schema_file_path"])