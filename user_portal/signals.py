from django.dispatch import receiver
from djoser.signals import user_activated

# @receiver(user_activated)
# def add_to_groups(user, request):
#     if user.is_admin:
