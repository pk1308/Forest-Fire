from datetime import datetime
import os

ROOT_DIR = os.getcwd()

CURRENT_TIME_STAMP = f"{datetime.now().strftime('%Y-%m-%d-%H')}"
# Variable declaration
# Data Ingestion related variables

DATASET_SCHEMA_COLUMNS_KEY = "columns"
DATASET_SCHEMA_TARGET_COLUMN_KEY = "target_column"
DATASET_SCHEMA_DOMAIN_VALUE_KEY = "domain_value"

DATA_INGESTION_ARTIFACT_DIR = "data_ingestion"
DATA_INGESTION_CONFIG_KEY = "data_ingestion_config"
DATA_INGESTION_DOWNLOAD_URL_KEY = "dataset_download_url"
DATA_INGESTION_RAW_DATA_DIR_KEY = "raw_data_dir"

DATA_INGESTION_DIR_NAME_KEY = "ingested_dir"
DATA_INGESTION_TRAIN_DIR_KEY = "ingested_train_dir"
DATA_INGESTION_TEST_DIR_KEY = "ingested_test_dir"
DATA_INGESTION_COLLECTION = "ingested_collection"
DATA_INGESTION_TRAIN_COLLECTION = "ingested_train_collection"
DATA_INGESTION_TEST_COLLECTION = "ingested_test_collection"

# Data Validation related variables
DATA_VALIDATION_CONFIG_KEY = "data_validation_config"
DATA_VALIDATION_SCHEMA_FILE_NAME_KEY = "schema_file_name"
DATA_VALIDATION_CONFIG_DIR = "validation_config_dir"

# Data Transformation related variables
DATA_TRANSFORMATION_ARTIFACT_DIR = "data_transformation"
DATA_TRANSFORMATION_CONFIG_KEY = "data_transformation_config"
DATA_TRANSFORMATION_DIR_NAME_KEY = "transformed_dir"
DATA_TRANSFORMATION_TRAIN_DIR_NAME_KEY = "transformed_train_dir"
DATA_TRANSFORMATION_TEST_DIR_NAME_KEY = "transformed_test_dir"
DATA_TRANSFORMATION_PREPROCESSING_DIR_KEY = "preprocessing_dir"
DATA_TRANSFORMATION_PREPROCESSED_FILE_NAME_KEY = "preprocessed_object_file_name"
PROCESSED_TRAIN_COLLECTION_KEY = "processed_train_collection"
PROCESSED_TEST_COLLECTION_KEY = "processed_test_collection"
# Model Training related variables

MODEL_TRAINER_ARTIFACT_DIR = "model_trainer"
MODEL_TRAINER_CONFIG_KEY = "model_trainer_config"
MODEL_TRAINER_DIR_KEY = "trained_model_dir"
MODEL_TRAINER_FILE_NAME_KEY = "model_file_name"
MODEL_TRAINER_BASE_ACCURACY_KEY = "base_accuracy"
RANDOMFOREST_PARAMS_CONFIG_KEY = "randomforest_params_config"
SVC_PARAMS_CONFIG_KEY = "svc_params_config"
GRADIENT_BOOSTING_PARAMS_CONFIG_KEY = "gradientboosting_params_config"

# Model Evaluation related variables

MODEL_EVALUATION_CONFIG_KEY = "model_evaluation_config"
MODEL_EVALUATION_FILE_NAME_KEY = "model_evaluation_file_name"
MODEL_EVALUATION_ARTIFACT_DIR = "model_evaluation"
# Model Pusher config key
MODEL_PUSHER_CONFIG_KEY = "model_pusher_config"
MODEL_PUSHER_MODEL_EXPORT_DIR_KEY = "model_export_dir"
PREPROCESSING_EXPORT_DIR_KEY = "preprocessing_export_dir"

# Training pipeline related variable
TRAINING_PIPELINE_CONFIG_KEY = "training_pipeline_config"
TRAINING_PIPELINE_ARTIFACT_DIR_KEY = "artifact_dir"
TRAINING_PIPELINE_NAME_KEY = "pipeline_name"

CONFIG_DIR = "config"
CONFIG_FILE_NAME = "config.yaml"
CONFIG_FILE_PATH = os.path.join(ROOT_DIR, CONFIG_DIR, CONFIG_FILE_NAME)

DATABASE_CONFIG_FILE_NAME = "database_config.yml"
DATABASE_CONFIG_FILE_PATH = os.path.join(ROOT_DIR, CONFIG_DIR, DATABASE_CONFIG_FILE_NAME)

KNN_KEY = 2
PROCEEDED_TRAIN_FILE_NAME = 'processed_train_file.csv'
PROCEEDED_TEST_FILE_NAME = 'processed_test_file.csv'

# model evaluation related variables
BEST_MODEL_KEY = "best_model"
HISTORY_KEY = "history"
MODEL_PATH_KEY = "model_path"
