from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class ValidateMixin(GenericViewSet):

    def process_serializer(self, data):
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return

        return self.handle_errors(serializer.errors)

    def handle_errors(self, errors):
        raise NotImplementedError()


class HTMLMixin(GenericViewSet):

    def render_response(self, data, response_serializer, many=False, status=HTTP_200_OK,
                        extra_context=None, **kwargs):
        serializer = response_serializer(
            data, many=many, context=self.get_serializer_context()
        )
        context = {
            'data': serializer.data
        }
        if extra_context is not None:
            context.update(extra_context)
        return Response(context, status=status, **kwargs)
