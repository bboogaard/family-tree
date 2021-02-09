import re

from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer


class HighlightBrowsableAPIRenderer(BrowsableAPIRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        data = super().render(data, accepted_media_type, renderer_context)
        return re.sub(r'~([^~]+)~', '<mark>\\1</mark>', data)


class HighlightJsonRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        data = self._apply_highlighting(
            data, renderer_context.get('search_query'))
        return super().render(data, accepted_media_type, renderer_context)

    def _apply_highlighting(self, data, search_query):
        if not search_query:
            return data

        if isinstance(data, list):
            result = []
            for item in data:
                result.append(self._apply_highlighting(item, search_query))
            return result
        elif isinstance(data, dict):
            result = {}
            for key, val in data.items():
                result[key] = self._apply_highlighting(val, search_query)
            return result
        elif isinstance(data, str):
            return re.sub(r'({})'.format(search_query), '~\\1~', data)
        else:
            return data
