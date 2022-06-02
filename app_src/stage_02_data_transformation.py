

import os
import sys
from app_util import read_yaml_file
import pandas as pd
import dill

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
from sklearn.compose import ColumnTransformer
from app_entity import DataTransformationArtifact

from app_util import save_object
from app_util.util import Read_data_MONGO
from app_config.constants import *
from app_logger.logger import App_Logger
from app_exception import AppException
from app_entity import DataTransformationConfig, DataIngestionArtifact, DataValidationArtifact

# columns:
#   Temperature: float
#   RH: float
#   Ws: float
#   Rain: float
#   FFMC: float
#   DMC: float
#   DC: float
#   ISI: float
#   BUI: float
#   Classes: category

Stage02_logger = App_Logger("Stage02_Data_Transformation")



class DataTransformation:

    def __init__(self, data_transformation_config: DataTransformationConfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact
                 ):
        """
        data_transformation_config: DataTransformationConfig
        data_ingestion_artifact: DataIngestionArtifact
        data_validation_artifact: DataValidationArtifact
        
        """
        try:
            Stage02_logger.info(f"{'=' * 20}Data Transformation log started.{'=' * 20} ")
            self.data_transformation_config = data_transformation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact

        except Exception as e:
            raise AppException(e, sys) from e

    @staticmethod
    def load_data(data_collection_conn, schema_file_path: str) -> pd.DataFrame:
        try:
            # reading the dataset schema file
            dataset_schema = read_yaml_file(schema_file_path)

            # extracting the columns info from the schema file
            schema = dataset_schema[DATASET_SCHEMA_COLUMNS_KEY]

            # reading the dataset
            dataframe =  Read_data_MONGO(Connection=data_collection_conn, Query={})
            error_message = ""
            for column in dataframe.columns:
                if column in list(schema.keys()):
                    dataframe[column].astype(schema[column])
                else:
                    error_message = f"{error_message} \nColumn: [{column}] is not in the schema."
            if len(error_message) > 0:
                raise Exception(error_message)
            return dataframe
        except Exception as e:
            raise AppException(e, sys) from e

    def get_data_transformer(self) -> ColumnTransformer:
        try:

            # reading schema file path
            schema_file_path = self.data_validation_artifact.schema_file_path
            data_transformation_config = self.data_transformation_config
            dataset_schema = read_yaml_file(schema_file_path)

            # splitting input columns and target column
            # TARGET_COLUMN
            target_column = dataset_schema[DATASET_SCHEMA_TARGET_COLUMN_KEY]

            # dropping categorical columns selecting only numerical columns to replace missing
            # value of numerical column
            columns = list(dataset_schema[DATASET_SCHEMA_COLUMNS_KEY].keys())
            columns.remove(target_column)

            # creating a pipeline to replace missing values
            neighbors =  data_transformation_config[KNN_KEY]
            num_pipeline = Pipeline(steps=[
                ('imputer', KNNImputer(n_neighbors=neighbors)),
                ('scaler', StandardScaler())])

            Stage02_logger.info(f"Numerical columns: {columns}")
            preprocessing = ColumnTransformer([
                ('num_pipeline', num_pipeline, columns),
            ])
            return preprocessing

        except Exception as e:
            raise AppException(e, sys) from e


    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            train_collection = self.data_validation_artifact.Train_collection
            test_collection= self.data_validation_artifact.Test_collection
            schema_file_path = self.data_validation_artifact.schema_file_path

            Stage02_logger.info(f"train file path: [{train_collection}]\n \
            test file path: [{test_collection}]\n \
            schema_file_path: [{schema_file_path}]\n. ")

            # # loading the dataset
            # Stage02_logger.info(f"Loading train and test dataset...")
            # train_dataframe = Read_data_MONGO(Connection=train_collection, Query={})
            # test_dataframe = Read_data_MONGO(Connection=test_collection, Query={})
            # loading the dataset
            Stage02_logger.info(f"Loading train and test dataset...")
            train_dataframe = DataTransformation.load_data(data_collection=train_collection,
                                                           schema_file_path=schema_file_path
                                                           )

            test_dataframe = DataTransformation.load_data(data_collection=train_collection,
                                                          schema_file_path=schema_file_path)
            

            Stage02_logger.info("Data loaded successfully.")

            target_column_name = read_yaml_file(file_path=schema_file_path)[DATASET_SCHEMA_TARGET_COLUMN_KEY]
            Stage02_logger.info(f"Target column name: [{target_column_name}].")
            

            # target_column
            Stage02_logger.info(f"Converting target column into numpy array.")
            train_target = train_dataframe[target_column_name]
            test_target = test_dataframe[target_column_name]
            Stage02_logger.info(f"Conversion completed target column into numpy array.")

            # dropping target column from the dataframe
            Stage02_logger.info(f"Dropping target column from the dataframe.")
            train_dataframe.drop(target_column_name, axis=1, inplace=True)
            test_dataframe.drop(target_column_name, axis=1, inplace=True)
            Stage02_logger.info(f"Dropping target column from the dataframe completed.")

            Stage02_logger.info(f"Creating preprocessing object.")
            preprocessing = self.get_data_transformer()
            Stage02_logger.info(f"Creating preprocessing object completed.")
            Stage02_logger.info(f"Preprocessing object learning started on training dataset.")
            Stage02_logger.info(f"Transformation started on training dataset.")
            train_input = pd.DataFrame(preprocessing.fit_transform(train_dataframe) , columns=train_dataframe.columns)
            Stage02_logger.info(f"Preprocessing object learning completed on training dataset.")

            Stage02_logger.info(f"Transformation started on testing dataset.")
            test_input = pd.DataFrame(preprocessing.transform(test_dataframe), columns=test_dataframe.columns)
            
            Stage02_logger.info(f"Transformation completed on testing dataset.")

            # adding target column back to the numpy array
            Stage02_logger.info("Started concatenation of target column back  into transformed numpy array.")
            train_data = pd.concat([train_input, train_target], axis=1)
            test_data = pd.concat([test_input, test_target], axis=1)
            Stage02_logger.info("Completed concatenation of  target column back  into transformed numpy array.")
            #########
            # saving the transformed dat

            transformed_train_dir = self.data_transformation_config.transformed_train_dir
            transformed_test_dir = self.data_transformation_config.transformed_test_dir
            transformed_train_file_path = os.path.join(transformed_train_dir, PROCEEDED_TRAIN_FILE_NAME)
            transformed_test_file_path = os.path.join(transformed_test_dir, PROCEEDED_TEST_FILE_NAME)
            Stage02_logger.info(f"Transformed train file path: [{transformed_train_file_path}].")
            Stage02_logger.info(f"Transformed test file path: [{transformed_test_file_path}].")
            # saving the transformed data 
            Stage02_logger.info(f"Saving transformed train and test dataset to file.")
            train_data.to_csv(transformed_train_file_path, index=False)
            test_data.to_csv(transformed_test_file_path, index=False)
            Stage02_logger.info(f"Saving transformed train and test dataset to file completed.")

            # writing the transformed data to mongo
            Stage02_logger.info(f"Writing transformed train and test dataset to mongo.")
            processes_train_collection = self.data_ingestion_artifact.processed_train_collection
            processes_test_collection = self.data_ingestion_artifact.processed_test_collection
            processes_train_collection.Insert_Many(train_data.to_dict('records'))
            processes_test_collection.Insert_Many(test_data.to_dict('records'))

            Stage02_logger.info(f"Saving preprocessing object")
            preprocessed_object_file_path = self.data_transformation_config.preprocessed_object_file_path
            # saving the preprocessed object
            save_object(file_path=preprocessed_object_file_path,
                        obj=preprocessing)
            Stage02_logger.info(f"Saving preprocessing object in file: [{preprocessed_object_file_path}] completed.")
            data_transformation_artifact = DataTransformationArtifact(is_transformed=True,
                                                                      message="Data transformed successfully",
                                                                      transformed_train_file_path=transformed_train_file_path,
                                                                      transformed_test_file_path=transformed_test_file_path,
                                                                      preprocessed_object_file_path=preprocessed_object_file_path ,
                                                                      train_collection=processes_train_collection,
                                                                      test_collection=processes_test_collection)
            Stage02_logger.info(f"Data Transformation artifact: [{data_transformation_artifact}] created successfully")
            return data_transformation_artifact

        except Exception as e:
            raise AppException(e, sys) from e

    def __del__(self):
    
        Stage02_logger.info(f"{'=' * 20}Data Transformation log ended.{'=' * 20} ")
