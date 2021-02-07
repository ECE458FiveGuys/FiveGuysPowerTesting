import unittest
import factory
from database.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'test_user_{}'.format(n))
    name = factory.Sequence(lambda n: 'Test User {}'.format(n))
    email = factory.Sequence(lambda n: 'test_user_{}@test.com'.format(n))
    password = factory.Faker('password')
    admin = factory.Faker('boolean')
    active = factory.Faker('boolean')


class MyTestCase(unittest.TestCase):
    def test_create(self):
        user = UserFactory.create()


    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
