import factory

from src.dto.tasks.task_criteria import TaskCriteriaCreateDTO, TaskCriteriaUpdateWeightDTO
from src.dto.tasks.tasks import TaskCreateDTO, TaskUpdateDTO


class TaskFactory(factory.Factory):
    class Meta:
        model = TaskCreateDTO

    workspace_id: int
    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph")


class TaskUpdateFactory(factory.Factory):
    class Meta:
        model = TaskUpdateDTO

    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph")
    is_active = True


class TaskCriteriaFactory(factory.Factory):
    class Meta:
        model = TaskCriteriaCreateDTO

    task_id: int
    criterion_id: int
    weight = factory.Faker("pyfloat", min_value=0.0, max_value=1.0)


class TaskCriteriaUpdateWeightFactory(factory.Factory):
    class Meta:
        model = TaskCriteriaUpdateWeightDTO

    weight = factory.Faker("pyfloat", min_value=0.0, max_value=1.0)
