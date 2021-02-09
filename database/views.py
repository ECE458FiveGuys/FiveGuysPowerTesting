from django.db.models import Q
from rest_framework import permissions
from rest_framework import viewsets, generics

from django_filters.rest_framework import DjangoFilterBackend

from database.models import EquipmentModel, Instrument, CalibrationEvent
from database.serializers import EquipmentModelSerializer, InstrumentSerializer, CalibrationEventSerializer, \
    VendorSerializer


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


class EquipmentModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = EquipmentModel.objects.all()
    serializer_class = EquipmentModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vendor']


# class EquipmentModelFilterList(generics.ListAPIView):
#     serializer_class = EquipmentModelSerializer
#
#     def get_queryset(self):
#         queryset = EquipmentModel.objects.all()
#         vendor = self.request.query_params.get('vendor', None)
#         if vendor is not None:
#             queryset = queryset.filter(equipmentmodel__vendor=vendor)
#         return queryset


class VendorAutoCompleteViewSet(generics.ListAPIView):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EquipmentModel.objects.filter(
            Q(vendor__contains=self.request.query_params.get('vendor'))
        )


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
