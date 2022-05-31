
import os
import sys
from app_config.configuration import ROOT_DIR

import pymongo

from app_logger.logger import App_Logger
from app_exception.exception import AppException
from app_util import read_yaml_file



lg = App_Logger("Database_operations")

ROOT_DIR = os.getcwd()
CONFIG_DIR = "config"
DATABASE_CONFIG_FILE_NAME = "database_config.yaml"
DATABASE_CONFIG_FILE_PATH = os.path.join(ROOT_DIR, CONFIG_DIR, DATABASE_CONFIG_FILE_NAME)
DATA_BASE_CONFIG = read_yaml_file(DATABASE_CONFIG_FILE_PATH)
CONNECTION_STRING = DATA_BASE_CONFIG["connection_string"]
DATABASE_NAME = DATA_BASE_CONFIG["database_name"]

class MongoDB:
    '''class for mongo db operations'''

    def __init__(self, Collection_Name):
        """Initialize the class with the database name and collection name
        the class initialization the class with the below argument 
        Args:
            Collection_Name : collection name
        """

        lg.debug('init function db %s collection %s', str(DATABASE_NAME), str(Collection_Name))
        

        lg.debug('get connection to mongo db')

        try:
            conn = pymongo.MongoClient(CONNECTION_STRING)
            lg.debug('connection to mongo db successful')
            self.__db = conn[DATABASE_NAME]
            self.__collection = self.__db[Collection_Name]

        except Exception as e:
            lg.error('error in get connection to mongo db %s', e)
            raise AppException(e, sys) from e
        lg.debug('connection to mongo db successful')

    def checkExistence_COL(self, COLLECTION_NAME):

        """It verifies the existence of collection name
        Collection_NAME: collection name
        returns True if collection exists else False"""

        collection_list = self.__db.list_collection_names()

        if COLLECTION_NAME in collection_list:
            lg.debug(f"Collection:'{COLLECTION_NAME}' in Database:'' exists")
            return True

        lg.error(f"Collection:'{COLLECTION_NAME}' in Database:' does not exists OR \n\
        no documents are present in the collection")
        return False


    def Insert_One(self, data):
        """insert one data into mongo dd
        Args:
            data (formated ): data to be inserted into mongo db
            
            {Key : Value}
            
        Returns:
            True if insertion is successful else False
        """
        try:
            self.__collection .insert_one(data)
        except Exception as e:
            lg.debug('error in insert data into mongo db %s', e)
            raise AppException(e, sys) from e
        lg.debug('insert data into mongo db successful%s')
        return True

    def Insert_Many(self, data):
        """insert many data into mongo dd
        Args:
            data (formated ): data to be inserted into mongo db
            
            {Key : Value}
            
        Returns:
            True if insertion is successful else False
        """
        lg.debug('insert many data into mongo db')
        try:
            self.__collection.insert_many(data)
        except Exception as e:
            lg.critical('error in insert many data into mongo db %s', e)
            print(e)
            raise AppException(e, sys) from e
        lg.debug('insert many data into mongo db successful')
        return True

    def Find_One(self, query={}):
        """find one data from mongo db
        if query is not provided then it will return the first document
        """

        lg.debug('find one data from mongo db')
        try:
            return self.__collection.find_one(query)
        except Exception as e:
            lg.critical('error in find one data from mongo db %s', e)
            raise AppException(e, sys) from e

    def Find_Many(self, query={}, limit=2000):
        """find many data from mongo db
        if query is not provided then it will return all the documents
        """

        try:
            lg.debug('find many data from mongo db')
            return self.__collection.find(query).limit(limit)
        except Exception as e:
            lg.critical('error in find many data from mongo db %s', e)
            return False

    def Drop_Collection(self, collection):
        """drop collection from mongo db
        Args:
            Collection: collection name to be dropped
           
        Returns:
            True if drop is successful else False"""

        if self.checkExistence_COL(collection):
            lg.debug('drop collection found in DB')
            try:
                lg.debug('drop collection from mongo db')
                self.__collection = self.__db[collection]
                self.collection.drop()
            except Exception as e:
                lg.critical('error in drop collection from mongo db %s', e)
                raise AppException(e, sys) from e
            lg.debug('drop collection from mongo db successful')
            return True
        else:
            lg.error('collection not present in the database')
            return 'collection not present in the database'



    if __name__ == '__main__':
        pass