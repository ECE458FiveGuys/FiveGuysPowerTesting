import abc

from database.services.service import Service

from django.core.exceptions import ObjectDoesNotExist

from database.exceptions import UserError, InactiveUserException, IllegalAccessException, AuthenticationFailedException
from database.models import User
from database.services.utils.security_utils import encrypt


def verify_and_retrieve_user(user_id, password):
    users = User.objects.filter(id=user_id)
    if users.count() == 0:
        raise UserError("No user with this id exists")
    try:
        user = users.get(password=encrypt(password))
        if not user.active:
            raise InactiveUserException()
        return user
    except ObjectDoesNotExist:
        raise AuthenticationFailedException()

class InAppService(Service):

    def __init__(self, user_id, password, admin_only):
        self.user = verify_and_retrieve_user(user_id, password)
        if admin_only and not self.user.admin:
            raise IllegalAccessException()
        super().__init__()

    @abc.abstractmethod
    def execute(self):
        pass
