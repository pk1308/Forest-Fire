from app_exception import AppException
from collections import namedtuple

DataIngestionConfig = namedtuple("DatasetConfig", ["dataset_download_url",
                                                   "raw_data_dir",
                                                   "ingested_train_dir",
                                                   "ingested_test_dir"
                                                   "raw_data_collection",
                                                   "ingested_train_collection",
                                                   "ingested_test_collection"])

DataValidationConfig = namedtuple("DataValidationConfig", ["schema_file_path"])

DataTransformationConfig = namedtuple("DataTransformationConfig", ["add_bedroom_per_room",
                                                                   "transformed_train_dir", "transformed_test_dir",
                                                                   "preprocessed_object_file_path"])