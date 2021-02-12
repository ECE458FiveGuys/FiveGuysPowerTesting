from djoser import serializers
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from user_portal.models import PowerUser


class ExtendedUserViewSet(viewsets.ModelViewSet):
    queryset = PowerUser.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = []

    @action(detail=True, methods=['get'])
    def deactivate(self, request, pk):
        user = PowerUser.objects.get(pk=pk)
        user.is_active = False
        user.save()
        user_serializer = serializers.UserSerializer(user)
        return Response(user_serializer.data)
