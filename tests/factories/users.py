import factory

from src.dto.users.user import UserCreateDTO


class UserFactory(factory.Factory):
    class Meta:
        model = UserCreateDTO

    fullname = factory.Faker("name")
    email = factory.Faker("email")
    password = factory.LazyAttribute(lambda o: "TestPass123!@#")
