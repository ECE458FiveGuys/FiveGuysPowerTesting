from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from database.exceptions import RequiredFieldsEmptyException, EntryDoesNotExistException
from database.model_enums import PostEnum
from database.services.user_services import UserDTO, create_user, deactivate_user, modify_user
from database.models import Model, Instrument, CalibrationEvent
from database.serializers import ModelSerializer, InstrumentSerializer, CalibrationEventSerializer


# class UserViewSet(viewsets.ViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def list(self, request):
#         queryset = User.objects.all()
#         serializer = UserSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, pk=None):
#         queryset = User.objects.all()
#         user = get_object_or_404(queryset, pk=pk)
#         serializer = UserSerializer(user)
#         return Response(serializer.data)
#
#     def create(self, request):
#         dto = self._build_dto_from_validated_data(request)
#         try:
#             create_user(dto)
#         except RequiredFieldsEmptyException:
#             return Response({'success': 'false'})
#         return Response({'success': 'true'})
#
#     @action(detail=True, methods=['put'], name='Delete User')
#     def delete_user(self, request, pk=None):
#         """Set user's active field to False"""
#         dto = self._build_dto_from_validated_data(request)
#         try:
#             deactivate_user(dto)
#         except EntryDoesNotExistException:
#             return Response({'success': 'false'})
#         return Response({'success': 'true'})
#
#     @action(detail=True, methods=['put'], name='Modify User')
#     def modify_user(self, request, pk=None):
#         """Change properties of user with specified id"""
#         dto = self._build_dto_from_validated_data(request)
#         try:
#             modify_user(dto)
#         except EntryDoesNotExistException:
#             return Response({'success': 'false'})
#         return Response({'success': 'true'})
#
#     def _build_dto_from_validated_data(self, request):
#         serializer = UserSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validated_data
#         return UserDTO(id=data['id'],
#                        username=data['username'],
#                        name=data['name'],
#                        email=data['email'],
#                        password=data['password'],
#                        admin=data['admin'],
#                        active=data['active'])


class ModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    permission_classes = [permissions.IsAuthenticated]


class InstrumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    permission_classes = [permissions.IsAuthenticated]


class CalibrationEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = CalibrationEvent.objects.all()
    serializer_class = CalibrationEventSerializer
    permission_classes = [permissions.IsAuthenticated]
