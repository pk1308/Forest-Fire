import os
import sys

from app_logger.logger import App_Logger
from app_exception.exception import AppException
from app_entity.artifact_entity import  DataIngestionArtifact, DataValidationArtifact
from app_entity.config_entity import DataValidationConfig
from app_database.mongoDB import MongoDB
from app_util.util import Read_data_MONGO


stage_01_logger = App_Logger("Stage_01_Data_Validation")

class DataValidation:
    def __init__(self, data_validation_config: DataValidationConfig,
                 data_ingestion_artifact: DataIngestionArtifact):
        try:
            stage_01_logger.info(f"{'='*20}Data Validation log started.{'='*20} ")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise AppException(e, sys) from e

    def is_train_test_exists(self) -> bool:
        try:
            is_train_exist = False
            is_test_exist = False
            train_collection = self.data_ingestion_artifact.Train_collection
            train_data = Read_data_MONGO(Connection=train_collection, Query={})
            test_collection = self.data_ingestion_artifact.Test_collection
            test_data = Read_data_MONGO(Connection=test_collection, Query={})
            stage_01_logger.info(f"Checking if train data exists: {len(train_data)}.")
            if len(train_data) > 0:
                is_train_exist = True
                stage_01_logger.info(f"Train data exists len: {len(train_data)}.")
            else:
                stage_01_logger.info(f"Train data does not exists: {len(train_data)}.")

            stage_01_logger.info(f"Checking if test data exists: {len(test_data)}.")
            if len(test_data) > 0:
                is_test_exist = True
                stage_01_logger.info(f"Test data exists: {len(test_data)}.")
            else:
                stage_01_logger.info(f"Test file does not exists: {test_data}.")
            return is_train_exist and is_test_exist
        except Exception as e:
            raise AppException(e, sys) from e

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            status = self.is_train_test_exists()
            message = "Data validation status: {}".format(status)
            data_validation_artifact = DataValidationArtifact(is_validated=status,
                                                              message=message,
                                                              schema_file_path=self.data_validation_config.schema_file_path,
                                                              Train_collection=self.data_ingestion_artifact.Train_collection,
                                                              Test_collection = self.data_ingestion_artifact.Test_collection)
            stage_01_logger.info(f"Data validation status: {status}.")
            stage_01_logger.info(
                f"Data validation artifact: {data_validation_artifact}.")
            return data_validation_artifact

        except Exception as e:
            raise AppException(e, sys) from e

    def __del__(self):
        stage_01_logger.info(f"{'='*20}Data Validation log ended.{'='*20} ")
