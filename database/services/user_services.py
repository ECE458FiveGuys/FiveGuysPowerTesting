from dataclasses import dataclass

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from database.model_enums import ModelsEnum, UserEnum
from database.exceptions import FieldCombinationNotUniqueException, RequiredFieldsEmptyException, EntryDoesNotExistException


@dataclass
class UserDTO:
    username: str
    name: str
    email: str
    password: str
    admin: bool
    active: bool
    id: int = 0


def create_user(dto):
    """
    Takes a UserDTO and adds user with specified values to database
    """
    try:
        if User.objects.filter(username=dto.power_username, name=dto.name, email=dto.email).count() > 0:
            raise FieldCombinationNotUniqueException(object_type=ModelsEnum.USER.value,
                                                     fields_list=[e.value for e in UserEnum])
        return User.objects.create(username=dto.power_username,
                                   name=dto.name,
                                   email=dto.email,
                                   password=dto.password,
                                   admin=dto.admin,
                                   active=dto.active)
    except IntegrityError:
        raise RequiredFieldsEmptyException(object_type=ModelsEnum.USER.value,
                                           required_fields_list=[e.value for e in UserEnum])


def modify_user(dto):
    """
    Takes a UserDTO and modifies the properties of user with the specified id
    """
    try:
        # check if username is taken as username must be unique
        count = User.objects.filter(username=dto.power_username).exclude(id=dto.id).count()
        if count == 1:
            raise FieldCombinationNotUniqueException(object_type=ModelsEnum.USER.value,
                                                     fields_list=[e.value for e in UserEnum])
        else:
            user = User.objects.filter(id=dto.id).get()
            user.power_username = dto.power_username
            user.name = dto.name
            user.email = dto.email
            user.password = dto.password
            user.admin = dto.admin
            user.active = dto.active
            user.save()
    except ObjectDoesNotExist:
        raise EntryDoesNotExistException(ModelsEnum.USER.value, dto.id)


def deactivate_user(dto):
    """
    Sets user's `active` value to False
    """
    try:
        user = User.objects.filter(id=dto.id).get()
        user.active = False
        user.save()
    except ObjectDoesNotExist:
        raise EntryDoesNotExistException(ModelsEnum.USER.value, dto.id)


def delete_user(dto):
    """
    Completely removes user from database
    """
    try:
        User.objects.filter(id=dto.id).get().delete()
    except ObjectDoesNotExist:
        raise EntryDoesNotExistException(ModelsEnum.USER.value, dto.id)
