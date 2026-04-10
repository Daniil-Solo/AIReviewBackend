import factory

from src.dto.tasks.tasks import TaskCreateDTO, TaskUpdateDTO


class TaskFactory(factory.Factory):
    class Meta:
        model = TaskCreateDTO

    workspace_id = factory.Faker("random_int", min=1, max=1000)
    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph")


class TaskUpdateFactory(factory.Factory):
    class Meta:
        model = TaskUpdateDTO

    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph")
    is_active = True
