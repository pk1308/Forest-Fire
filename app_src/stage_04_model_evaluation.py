from app_entity.artifact_entity import DataTransformationArtifact
from app_logger.logger import App_Logger
from app_exception.exception import AppException
from app_entity.artifact_entity import  ModelTrainerArtifact, DataIngestionArtifact, DataValidationArtifact,\
                                        ModelEvaluationArtifact
from app_entity.config_entity import ModelEvaluationConfig
from app_config.constants import *
import numpy as np
import os
import sys
from app_util.util import write_yaml_file, read_yaml_file, load_object
from app_src.stage_02_data_transformation import DataTransformation
from app_src.stage_03_model_trainer import  ModelTrainer

stage_04_logger = App_Logger(__name__)


class ModelEvaluation:

    def __init__(self, model_evaluation_config: ModelEvaluationConfig,
                 data_validation_artifact: DataValidationArtifact,
                 model_trainer_artifact: ModelTrainerArtifact,
                 data_transformation_artifact: DataTransformationArtifact):
        try:
            stage_04_logger.info(f"{'=' * 20}Model Evaluation log started.{'=' * 20} ")
            self.model_evaluation_config = model_evaluation_config
            self.model_trainer_artifact = model_trainer_artifact
            self.data_transformation_artifact = data_transformation_artifact
            self.data_validation_artifact = data_validation_artifact
        except Exception as e:
            raise AppException(e, sys) from e

    def get_best_model(self):
        try:
            model = None
            model_evaluation_file_path = self.model_evaluation_config.model_evaluation_file_path

            if not os.path.exists(model_evaluation_file_path):
                write_yaml_file(file_path=model_evaluation_file_path,
                                )
                return model
            model_eval_file_content = read_yaml_file(file_path=model_evaluation_file_path)

            model_eval_file_content = dict() if model_eval_file_content is None else model_eval_file_content

            if BEST_MODEL_KEY not in model_eval_file_content:
                return model

            model = load_object(file_path=model_eval_file_content[BEST_MODEL_KEY][MODEL_PATH_KEY])
            return model
        except Exception as e:
            raise AppException(e, sys) from e

    def update_evaluation_report(self, model_evaluation_artifact: ModelEvaluationArtifact):
        try:
            eval_file_path = self.model_evaluation_config.model_evaluation_file_path
            model_eval_content = read_yaml_file(file_path=eval_file_path)
            model_eval_content = dict() if model_eval_content is None else model_eval_content
            previous_best_model = None
            if BEST_MODEL_KEY in model_eval_content:
                previous_best_model = model_eval_content[BEST_MODEL_KEY]

            stage_04_logger.info(f"Previous eval result: {model_eval_content}")
            eval_result = {
                BEST_MODEL_KEY: {
                    MODEL_PATH_KEY: model_evaluation_artifact.evaluated_model_path,
                }
            }

            if previous_best_model is not None:
                model_history = {self.model_evaluation_config.time_stamp: previous_best_model}
                if HISTORY_KEY not in model_eval_content:
                    history = {HISTORY_KEY: model_history}
                    eval_result.update(history)
                else:
                    model_eval_content[HISTORY_KEY].update(model_history)

            model_eval_content.update(eval_result)
            stage_04_logger.info(f"Updated eval result:{model_eval_content}")
            write_yaml_file(file_path=eval_file_path, data=model_eval_content)

        except Exception as e:
            raise AppException(e, sys) from e

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        try:
            trained_model_file_path = self.model_trainer_artifact.trained_model_file_path
            trained_model_object = load_object(file_path=trained_model_file_path)

            train_collection = self.data_validation_artifact.Train_collection
            test_collection = self.data_validation_artifact.Test_collection

            schema_file_path = self.data_validation_artifact.schema_file_path

            train_dataframe = DataTransformation.load_data(data_collection_conn=train_collection,
                                                           schema_file_path=schema_file_path
                                                           )

            test_dataframe = DataTransformation.load_data(data_collection_conn=test_collection,
                                                          schema_file_path=schema_file_path)
            schema_content = read_yaml_file(file_path=schema_file_path)
            target_column_name = schema_content[DATASET_SCHEMA_TARGET_COLUMN_KEY]
            # column = schema_content[DATASET_SCHEMA_COLUMNS_KEY]
            # column_names = column.keys()
            preprocessed_object=self.data_transformation_artifact.preprocessed_object


            # target_column
            stage_04_logger.info(f"Converting target column into numpy array.")
            train_target_arr = train_dataframe[target_column_name]
            test_target_arr = test_dataframe[target_column_name]
            stage_04_logger.info(f"Conversion completed target column into numpy array.")

            # dropping target column from the dataframe
            stage_04_logger.info(f"Dropping target column from the dataframe.")
            train_dataframe.drop(target_column_name, axis=1, inplace=True)
            test_dataframe.drop(target_column_name, axis=1, inplace=True)
            stage_04_logger.info(f"Dropping target column from the dataframe completed.")
            
            # columns transformation
            train_dataframe[train_dataframe.columns] = preprocessed_object.transform(train_dataframe)
            test_dataframe[test_dataframe.columns] = preprocessed_object.transform(test_dataframe)

            model = self.get_best_model()

            if model is None:
                stage_04_logger.info("Not found any existing model. Hence accepting trained model")
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=True)
                self.update_evaluation_report(model_evaluation_artifact)
                stage_04_logger.info(f"Model accepted. Model eval artifact {model_evaluation_artifact} created")
                return model_evaluation_artifact

            model_list = [model, trained_model_object]

            metric_info_artifact = ModelTrainer.evaluate_model(model_list=model_list,
                                                               X_train=train_dataframe,
                                                               y_train=train_target_arr,
                                                               X_test=test_dataframe,
                                                               y_test=test_target_arr,
                                                               base_accuracy=self.model_trainer_artifact.model_accuracy,
                                                               )
            stage_04_logger.info(f"Model evaluation completed. model metric artifact: {metric_info_artifact}")

            if metric_info_artifact is None:
                response = ModelEvaluationArtifact(is_model_accepted=False,
                                                   evaluated_model_path=trained_model_file_path ,
                                                   preprocessed_object=preprocessed_object
                                                   )
                stage_04_logger.info(response)
                return response

            if metric_info_artifact.index_number == 1:
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=True)
                self.update_evaluation_report(model_evaluation_artifact)
                stage_04_logger.info(f"Model accepted. Model eval artifact {model_evaluation_artifact} created")

            else:
                stage_04_logger.info("Trained model is no better than existing model hence not accepting trained model")
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=False)
            return model_evaluation_artifact
        except Exception as e:
            raise AppException(e, sys) from e

    def __del__(self):
        stage_04_logger.info(f"{'=' * 20}Model Evaluation log completed.{'=' * 20} ")
