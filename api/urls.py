from django.urls import re_path

from api.views import SearchNamesView, SearchTextView

urlpatterns = [
    re_path(r'^search/names', SearchNamesView.as_view()),
    re_path(r'^search/text', SearchTextView.as_view()),
]
