import yaml,os,sys
import dill
import pandas as pd 

from app_logger.logger import App_Logger
from app_exception.exception import AppException



util_logger = App_Logger('util_logger')

def write_yaml_file(file_path,data=None):
    """
    Create yaml file 
    file_path: str
    data: dict
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path,"w") as yaml_file:
            if data is not None:
                yaml.dump(data,yaml_file)
    except Exception as e:
        raise AppException(e,sys) from e


def read_yaml_file(file_path:str)->dict:
    """
    Reads a YAML file and returns the contents as a dictionary.
    file_path: str
    """
    try:
        with open(file_path, 'rb') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise AppException(e,sys) from e

def save_object(file_path:str,obj):
    """
    file_path: str
    obj: Any sort of object
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)
    except Exception as e:
        raise AppException(e,sys) from e


def load_object(file_path:str):
    """
    file_path: str
    """
    try:
        with open(file_path, "rb") as file_obj:
            return dill.load(file_obj)

    except Exception as e:
        raise AppException(e,sys) from e


def Read_data_MONGO(Connection  , Del_id = True , Query = {}):
    """ This function take the connection object and read the data from the database and return the dataframe
    """
    util_logger.info("Reading the data from the database")
    try:
        data = Connection.Find_Many(query=Query)
    except Exception as e:
        raise AppException(e,sys) from e
    dataFrame = pd.DataFrame(list(data))
    util_logger.info("Dataframe created successfully")
    if Del_id:
         dataFrame.drop(['_id'], axis=1, inplace=True)
    return  dataFrame