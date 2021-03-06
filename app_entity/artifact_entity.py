from collections import namedtuple

DataIngestionArtifact = namedtuple("DataIngestionArtifact", [
    "train_file_path", "test_file_path", "is_ingested", "message"])

DataValidationArtifact = namedtuple("DataValidationArtifact", [
    "is_validated", "message", "schema_file_path", "Train_collection", "Test_collection"])

DataTransformationArtifact = namedtuple("DataTransformationArtifact", ["is_transformed",
                                                                       "message", "transformed_train_file_path",
                                                                       "transformed_test_file_path",
                                                                       "preprocessed_object_file_path",
                                                                       "preprocessed_object",
                                                                       "train_collection", "test_collection"])

ModelTrainerArtifact = namedtuple("ModelTrainerArtifact", ["is_trained", "message", "trained_model_file_path",
                                                           "train_precision", "test_precision", "train_accuracy", "test_accuracy",
                                                           "model_accuracy"])

ModelEvaluationArtifact = namedtuple("ModelEvaluationArtifact", ["is_model_accepted", "evaluated_model_path"])

ModelPusherArtifact = namedtuple("ModelPusherArtifact", ["is_model_pusher", "export_model_file_path" ,
                                                         "columns_transformer_file_path"])

MetricInfoArtifact = namedtuple("MetricInfo",
                                ["model_name", "model_object", "train_precision", "test_precision", "train_accuracy",
                                 "test_accuracy", "model_accuracy", "index_number"])
