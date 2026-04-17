import factory

from src.dto.transactions.transactions import AdminTopUpDTO


class TransactionFactory(factory.Factory):
    class Meta:
        model = AdminTopUpDTO

    user_id = factory.Sequence(lambda n: n)
    amount = factory.Faker("pyfloat", min_value=100, max_value=10000)
