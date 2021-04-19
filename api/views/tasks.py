from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.serializers import task_serializer_factory


class TaskViewSet(GenericViewSet):

    permission_classes = [IsAuthenticated]

    @action(methods=['get'], detail=False, url_path='(?P<command>[^/.]+)')
    def run_command(self, request, command, *args, **kwargs):
        self.serializer_class = task_serializer_factory(command)
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()
