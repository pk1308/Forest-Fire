from ctypes import util
from nbformat import write
from numpy import save
from app_logger.logger import ROOT_DIR, App_Logger
from app_exception.exception import AppException
from app_entity.artifact_entity import ModelPusherArtifact, ModelEvaluationArtifact , DataIngestionArtifact , DataTransformationArtifact
from app_entity.config_entity import ModelPusherConfig
from app_util.util import save_object , write_yaml_file
import os
import sys
import shutil

stage_05_logger = App_Logger(__name__)


class ModelPusher:

    def __init__(self, model_pusher_config: ModelPusherConfig,
                 model_evaluation_artifact: ModelEvaluationArtifact,
                 data_transformation_artifact: DataTransformationArtifact):
        try:
            stage_05_logger.info(f"{'=' * 20}Model Pusher log started.{'=' * 20} ")
            self.model_pusher_config = model_pusher_config
            self.model_evaluation_artifact = model_evaluation_artifact
            self.data_transformation_artifact=data_transformation_artifact

        except Exception as e:
            raise AppException(e, sys) from e

    def export_model(self) -> ModelPusherArtifact:
        try:
            evaluated_model_file_path = self.model_evaluation_artifact.evaluated_model_path
            model_export_dir = self.model_pusher_config.model_export_dir_path
            model_file_name = os.path.basename(evaluated_model_file_path)
            export_model_file_path = os.path.join(model_export_dir, model_file_name)
            stage_05_logger.info(f"Exporting model file: [{export_model_file_path}]")
            os.makedirs(model_export_dir, exist_ok=True)

            preprocessing_export_dir = self.model_pusher_config.preprocessing_export_dir_path
            preprocessing_export_dir_path = os.path.join(preprocessing_export_dir,"column_transformer.pkl")

            preprocessing = self.data_transformation_artifact.preprocessed_object
            save_object(file_path=preprocessing_export_dir_path,obj=preprocessing)

            shutil.copy(src=evaluated_model_file_path, dst=export_model_file_path)
            stage_05_logger.info(
                f"Trained model: {evaluated_model_file_path} is copied in export dir:[{export_model_file_path}]")

            model_pusher_artifact = ModelPusherArtifact(is_model_pusher=True,
                                                        export_model_file_path=export_model_file_path,
                                                        columns_transformer_file_path= preprocessing_export_dir_path)
            stage_05_logger.info(f"Model pusher artifact: [{model_pusher_artifact}]")

            write_yaml_file(file_path=os.path.join(ROOT_DIR,"model_pusher_artifact.yaml"), data = model_pusher_artifact)

            return model_pusher_artifact
        except Exception as e:
            raise AppException(e, sys) from e

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        try:
            return self.export_model()
        except Exception as e:
            raise AppException(e, sys) from e

    def __del__(self):
        stage_05_logger.info(f"{'=' * 20}Model Pusher log completed.{'=' * 20} ")
