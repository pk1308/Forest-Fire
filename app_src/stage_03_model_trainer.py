from cgi import test
import os
import sys

from app_logger.logger import App_Logger
from app_exception.exception import AppException
from app_entity.config_entity import ModelTrainerConfig
from app_entity.artifact_entity import DataTransformationArtifact, MetricInfoArtifact, ModelTrainerArtifact
from app_src.stage_02_data_transformation import DataTransformation
from sklearn.metrics import accuracy_score, precision_score, recall_score
from app_util.util import load_object, save_object, Read_data_MONGO
from app_database.mongoDB import MongoDB

model_trainer_logger = App_Logger(__name__)


class TrainedModel:
    def __init__(self, preprocessing_object, trained_model_object):
        """
        TrainedModel constructor
        preprocessing_object: preprocessing_object
        trained_model_object: trained_model_object
        """
        self.preprocessing_object = preprocessing_object
        self.trained_model_object = trained_model_object

    def predict(self, X):
        """
        function accepts raw inputs and then transformed raw input using preprocessing_object
        which guarantees that the inputs are in the same format as the training data
        At last it perform prediction on transformed features
        """
        
        return self.trained_model_object.predict(X)

    def __repr__(self):
        return f"{type(self.trained_model_object).__name__}()"

    def __str__(self):
        return f"{type(self.trained_model_object).__name__}()"


class ModelTrainer:

    def __init__(self, model_trainer_config: ModelTrainerConfig,
                 data_transformation_artifact: DataTransformationArtifact):
        try:
            model_trainer_logger.info(f"{'=' * 20}Model trainer log started.{'=' * 20} ")
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
            self.model_list = self.model_trainer_config.model_list
        except Exception as e:
            raise AppException(e, sys) from e

    def fit(self, X, y):
        try:
            for model in self.model_list:
                model_trainer_logger.info(
                    f"Started training model: [{type(model).__name__}]")
                model.fit(X, y)
                model_trainer_logger.info(
                    f"Finished training model: [{type(model).__name__}]")

        except Exception as e:
            raise AppException(e, sys) from e

    @staticmethod
    def evaluate_model(model_list: list, X_train, y_train, X_test, y_test, base_accuracy=0.5) -> MetricInfoArtifact:
        try:
            index_number = 0
            metric_info_artifact = None
            for model in model_list:
                model_name = str(model)
                model_trainer_logger.info(
                    f"Started evaluating model: [{type(model).__name__}]")
                y_train_pred = model.predict(X_train)
                y_test_pred = model.predict(X_test)

                train_acc = accuracy_score(y_train, y_train_pred)
                test_acc = accuracy_score(y_test, y_test_pred)
                train_precision = precision_score(y_train, y_train_pred)
                test_precision = precision_score(y_test, y_test_pred)

                # Calculating harmonic mean of train_accuracy and test_accuracy
                model_accuracy = (2 * (train_acc * test_acc)) / (train_acc + test_acc)
                diff_test_train_acc = abs(test_acc - train_acc)
                message = f"{'*' * 20}{model_name} metric info{'*' * 20}"
                model_trainer_logger.info(f"{message}")

                message = f"\n\t\tTrain accuracy: [{train_acc}]."
                message += f"\n\t\tTest accuracy: [{test_acc}]."
                message += f"\n\t\tTrain Precision: [{test_precision}]."
                message += f"\n\t\tTest Precision: [{test_precision}]."
                message += f"\n\t\tModel accuracy: [{model_accuracy}]."
                message += f"\n\t\tBase accuracy: [{base_accuracy}]."
                message += f"\n\t\tDiff test train accuracy: [{diff_test_train_acc}]."
                model_trainer_logger.info(message)
                message = f"{'*' * 20}{model_name} metric info{'*' * 20}"
                model_trainer_logger.info(message)

                if model_accuracy >= base_accuracy and diff_test_train_acc < 0.05:
                    base_accuracy = model_accuracy
                    metric_info_artifact = MetricInfoArtifact(model_name=model_name,
                                                              model_object=model,
                                                              train_precision=train_precision,
                                                              test_precision=test_precision,
                                                              train_accuracy=train_acc,
                                                              test_accuracy=test_acc,
                                                              model_accuracy=model_accuracy,
                                                              index_number=index_number)

                    model_trainer_logger.info(
                        f"Acceptable model found {metric_info_artifact}. ")
                index_number += 1

            if metric_info_artifact is None:
                model_trainer_logger.info(
                    f"No model found with higher accuracy than base accuracy")

            return metric_info_artifact
        except Exception as e:
            raise AppException(e, sys) from e

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:

            train_file_collection = self.model_trainer_config.train_collection
            test_file_collection = self.model_trainer_config.test_collection
            test_dataset = Read_data_MONGO(test_file_collection)
            train_dataset = Read_data_MONGO(train_file_collection)

            X_train, y_train = train_dataset.iloc[:, :-1], train_dataset.iloc[:, -1]
            X_test, y_test = test_dataset.iloc[:, :-1], test_dataset.iloc[:, -1]

            self.fit(X_train, y_train)
            model_metric_artifact = ModelTrainer.evaluate_model(model_list=self.model_list,
                                                                X_train=X_train,
                                                                y_train=y_train,
                                                                X_test=X_test,
                                                                y_test=y_test,
                                                                base_accuracy=self.model_trainer_config.base_accuracy)

            if model_metric_artifact is None:
                raise Exception("None of suggested model is able to achieve least base accuracy")
            preprocessed_object_file_path = self.data_transformation_artifact.preprocessed_object_file_path

            preprocessed_object = load_object(
                file_path=preprocessed_object_file_path)

            trained_model = TrainedModel(
                preprocessing_object=preprocessed_object,
                trained_model_object=model_metric_artifact.model_object)

            trained_model_path = self.model_trainer_config.trained_model_file_path
            model_trainer_logger.info(f"Saving trained model to: {trained_model_path}")
            save_object(file_path=trained_model_path, obj=trained_model)
            model_trainer_logger.info(f"Saved trained model to: {trained_model_path}")

            response = ModelTrainerArtifact(is_trained=True,
                                            message="Model trained successfully",
                                            trained_model_file_path=trained_model_path,
                                            train_precision=model_metric_artifact.train_precision,
                                            test_precision=model_metric_artifact.test_precision,
                                            train_accuracy=model_metric_artifact.train_accuracy,
                                            test_accuracy=model_metric_artifact.test_accuracy,
                                            model_accuracy=model_metric_artifact.model_accuracy
                                            )
            model_trainer_logger.info(f"Trained model artifact: {response}.")
            return response
        except Exception as e:
            raise AppException(e, sys) from e

    def __del__(self):
        model_trainer_logger.info(f"{'=' * 20}Model trainer log completed.{'=' * 20} ")
