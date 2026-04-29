import factory

from src.constants.ai_pipeline import PipelineStepEnum
from src.dto.custom_models import TaskStepsModelRequestCreateDTO
from src.dto.custom_models.custom_models import CustomModelRequestCreateDTO, CustomModelRequestUpdateDTO


class CustomModelFactory(factory.Factory):
    class Meta:
        model = CustomModelRequestCreateDTO

    name = factory.Faker("word")
    model = factory.Faker("word")
    base_url = factory.Faker("url")
    api_key = factory.Faker("word")


class CustomModelUpdateFactory(factory.Factory):
    class Meta:
        model = CustomModelRequestUpdateDTO

    name = factory.Faker("word")
    model = factory.Faker("word")
    base_url = factory.Faker("url")
    api_key = factory.Faker("word")


class TaskStepsModelFactory(factory.Factory):
    class Meta:
        model = TaskStepsModelRequestCreateDTO

    steps = {step: None for step in PipelineStepEnum}
