import factory

from src.dto.criteria.criteria import CriterionCreateDTO


class CriterionFactory(factory.Factory):
    class Meta:
        model = CriterionCreateDTO

    description = factory.Faker("sentence", nb_words=10)
    tags = factory.LazyAttribute(lambda o: ["api"])
    stage = None
    workspace_id: int | None = None
    task_id: int | None = None