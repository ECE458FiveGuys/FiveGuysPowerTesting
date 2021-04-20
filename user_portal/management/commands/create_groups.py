"""
Permission: An ability on the system that can be conferred upon a user. Users can be given one or more permissions
by users that have the administrator permission. Authenticated users with none of the permissions below are deemed
“unprivileged users”; such users may view (but not modify) models and instrument information. The grantable permissions
are:
    • Instrument management permission: Allows creation, modification, and deletion of instruments. This also includes
    management of instrument categories. This does not confer the ability to calibrate an instrument.
    • Model management permission: Allows creation, modification, and deletion of models. This also includes management
    of model categories. This permission implies instrument management permission.
    • Calibration permission: Allows the user to perform calibrations.
    • Administrator permission: Inherits all of the abilities described above. Can also confer or revoke permissions
    onto users (per req 1.10).
"""
import logging

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from database.models.instrument import CalibrationEvent, Instrument, InstrumentCategory, ApprovalData
from database.models.model import Model, ModelCategory
from user_portal.models import User
from user_portal.enums import PermissionGroupEnum

GROUP_PERMISSIONS = {
    PermissionGroupEnum.UNPRIVILEGED.value: {
        Model: ['view'],
        Instrument: ['view'],
        ModelCategory: ['view'],
        InstrumentCategory: ['view'],
        CalibrationEvent: ['view'],
        ApprovalData: ['view'],
        User: ['view'],
    },
    PermissionGroupEnum.INSTRUMENT_MANAGEMENT.value: {
        Model: ['view'],
        Instrument: ['add', 'change', 'delete', 'view'],
        ModelCategory: ['view'],
        InstrumentCategory: ['add', 'change', 'delete', 'view'],
        CalibrationEvent: ['view'],
        ApprovalData: ['view'],
        User: ['view'],
    },
    PermissionGroupEnum.MODEL_MANAGEMENT.value: {
        Model: ['add', 'change', 'delete', 'view'],
        Instrument: ['add', 'change', 'delete', 'view'],
        ModelCategory: ['add', 'change', 'delete', 'view'],
        InstrumentCategory: ['add', 'change', 'delete', 'view'],
        CalibrationEvent: ['view'],
    ApprovalData: ['view'],
        User: ['view'],
    },
    PermissionGroupEnum.CALIBRATION.value: {
        Model: ['view'],
        Instrument: ['view'],
        ModelCategory: ['view'],
        InstrumentCategory: ['view'],
        CalibrationEvent: ['add', 'change', 'delete', 'view'],
        ApprovalData: ['view'],
        User: ['view'],
    },
    PermissionGroupEnum.CALIBRATION_APPROVER.value: {
        Model: ['view'],
        Instrument: ['view'],
        ModelCategory: ['view'],
        InstrumentCategory: ['view'],
        CalibrationEvent: ['add', 'change', 'delete', 'view'],
        ApprovalData:  ['add', 'change', 'delete', 'view'],
        User: ['view'],
    },
    PermissionGroupEnum.ADMINISTRATOR.value: {
        Model: ['add', 'change', 'delete', 'view'],
        Instrument: ['add', 'change', 'delete', 'view'],
        ModelCategory: ['add', 'change', 'delete', 'view'],
        InstrumentCategory: ['add', 'change', 'delete', 'view'],
        CalibrationEvent: ['add', 'change', 'delete', 'view'],
        ApprovalData:  ['add', 'change', 'delete', 'view'],
        User: ['add', 'change', 'delete', 'view'],
    },
}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Creates permission groups for users'

    def handle(self, *args, **options):
        for group_name in GROUP_PERMISSIONS:
            group, created = Group.objects.get_or_create(name=group_name)
            for model_cls in GROUP_PERMISSIONS[group_name]:
                for perm_index, perm_name in enumerate(GROUP_PERMISSIONS[group_name][model_cls]):
                    # Generate permission name as Django would generate it
                    codename = f'{perm_name}_{model_cls._meta.model_name}'
                    try:
                        perm = Permission.objects.get(codename=codename)
                        group.permissions.add(perm)
                        print(f'Adding {codename} to group {group}.')
                    except Permission.DoesNotExist:
                        logging.warning(f'Permission not found with name {codename}.')
        print('Created default group and permissions.')
