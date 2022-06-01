
import sys
import os

from six.moves import urllib
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit

from app_entity.artifact_entity import DataIngestionArtifact
from app_logger.logger import App_Logger
from app_exception.exception import AppException
from app_entity.config_entity import DataIngestionConfig

Stage0_logger = App_Logger('Stage0_logger')


class DataIngestion:
    

    def __init__(self, data_ingestion_config: DataIngestionConfig):
        """
        DataIngestion Initialization
        data_ingestion_config: DataIngestionConfig 
        """
        try:
            Stage0_logger.info(f"{'='*20}Data Ingestion log started.{'='*20} ")
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise AppException(e, sys) from e



    def download_data(self):
        """
        Fetch housing data from the url
        
        """
        try:
            
            forest_dataset_url = self.data_ingestion_config.dataset_download_url
            Raw_data_dir = self.data_ingestion_config.raw_data_dir
            os.makedirs(Raw_data_dir, exist_ok=True)
            forest_file_name = os.path.basename(forest_dataset_url)
            raw_file_path = os.path.join(Raw_data_dir, forest_file_name)
            Stage0_logger.info(f"Downloading housing data from {forest_dataset_url} into file {raw_file_path}")
            urllib.request.urlretrieve(forest_dataset_url,raw_file_path)
            Stage0_logger.info(f"Downloaded housing data from {forest_dataset_url} into file {raw_file_path}")
            return raw_file_path
        except Exception as e:
            raise AppException(e, sys) from e

    def split_data_as_train_test(self)->DataIngestionArtifact:
        try:
            data_ingestion_config = self.data_ingestion_config
            raw_data_dir = data_ingestion_config.raw_data_dir

            #there is only one file in tgz hence we can use os.listdir to get the file name
            file_name = os.listdir(raw_data_dir)[0]
            forest_file_path = os.path.join(raw_data_dir, file_name)
            
            
            #Reading csv file using pandas
            Stage0_logger.info(f"Reading csv file: [{forest_file_path }]")
            forest_data_frame = pd.read_csv(forest_file_path  , header=1)



            Stage0_logger.info(f"Splitting data into train and test")

            # strip the column name of space 
            forest_data_frame.columns = [columns.strip() for columns  in forest_data_frame.columns.to_list() ] 

            # drop row 122 , 123 
            Stage0_logger.debug("Data to drop column No : 122,123 as its the area name : {}".\
                format(forest_data_frame.iloc[122:123].to_dict()))
            forest_data_frame.drop([122,123], axis=0, inplace=True)
            forest_data_frame['FWI']=forest_data_frame['FWI'].apply(lambda x: x.replace('fire   ','NaN'))
            forest_data_frame['Classes'].fillna('Fire', inplace=True)
            
            Data_Region = forest_data_frame.iloc[1:122 , :].copy()
            Data_Region1 = forest_data_frame.iloc[122: , :].copy()

            
            Data_Region_Dummy = pd.read_csv(forest_file_path)
            Region1 = Data_Region_Dummy.columns.to_list()[0].strip()
            Stage0_logger.info("Region1 is : {}".format(Region1))
            Data_Region_Dummy1 =  pd.read_csv(forest_file_path  , header=1 )
            Region2 = Data_Region_Dummy1.iloc[122]['day']
            Stage0_logger.info("Region2 is : {}".format(Region2))
            
            Data_Region["forest"] = Region1
            Data_Region1["forest"] = Region2

            forest_data_frame_strat = Data_Region.append(Data_Region1 , ignore_index=True)
            #Splitting data into train and test
            strat_train_set = None
            strat_test_set = None
            split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

            for train_index, test_index in split.split(forest_data_frame_strat, forest_data_frame_strat["forest"]):
                strat_train_set = forest_data_frame_strat.loc[train_index].drop(["forest" , "day" , "month" , "year" ],\
                    axis=1)
                strat_test_set = forest_data_frame_strat.loc[test_index].drop(["forest" , "day" , "month" , "year" ],\
                    axis=1)

            #saving the train and test dataframes   
            train_file_path = os.path.join(data_ingestion_config.ingested_train_dir, file_name)
            test_file_path = os.path.join(data_ingestion_config.ingested_test_dir, file_name)

            if strat_train_set is not None:
                os.makedirs(data_ingestion_config.ingested_train_dir, exist_ok=True)
                
                Stage0_logger.info(f"Exporting training datset to file: [{train_file_path}]")
                strat_train_set.to_csv(train_file_path, index=False)
                strat_train_set_dict = strat_train_set.to_dict( orient='records')
                data_ingestion_config.ingested_train_collection.Insert_Many(strat_train_set_dict)
            
            if strat_test_set is not None:
                os.makedirs(data_ingestion_config.ingested_test_dir, exist_ok=True)
                
                Stage0_logger.info(f"Exporting test dataset to file: [{test_file_path}]")
                strat_test_set.to_csv(test_file_path, index=False)
                strat_test_set_dict = strat_test_set.to_dict( orient='records')
                data_ingestion_config.ingested_test_collection.Insert_Many(strat_test_set_dict)

            forest_data_frame_strat_dict = forest_data_frame_strat.to_dict( orient='records')
            data_ingestion_config.raw_data_collection.Insert_Many(forest_data_frame_strat_dict)
                

            data_ingestion_artifact = DataIngestionArtifact(train_file_path=train_file_path,
            test_file_path=test_file_path,
            is_ingested=True,
            message="Data Ingestion completed and data set has been splited into train and test")
            Stage0_logger.info(f"Data Ingestion artifact:[{data_ingestion_artifact}]")

            return data_ingestion_artifact

        except Exception as e:
            raise AppException(e, sys) from e

    def initiate_data_ingestion(self) ->DataIngestionArtifact:
        try:
            self.download_data()
            return self.split_data_as_train_test()
        except Exception as e:
            raise AppException(e, sys) from e

    def __del__(self):
        Stage0_logger.info(f"{'='*20}Data Ingestion log completed.{'='*20} \n\n")