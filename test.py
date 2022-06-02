from app_logger.logger import App_Logger
from app_pipeline.training_pipeline import TrainingPipeline

if __name__ == '__main__':
    test_log = App_Logger(__name__)
    try:
        TrainingPipeline().start_training_pipeline()
    except Exception as e:
        test_log.info(e)