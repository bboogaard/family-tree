from django.shortcuts import redirect
from django.views.generic.base import ContextMixin, TemplateResponseMixin, View

from lib.api import call_api
from lib.auth import login_protected


class FormView(ContextMixin, TemplateResponseMixin, View):

    form_class = None

    template_name = None

    def get(self, request, *args, **kwargs):
        form = self.get_form(initial=self.get_form_initial())
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST, initial=self.get_form_initial())
        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        raise NotImplementedError()

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form(self, data=None, **kwargs):
        form_class = self.get_form_class()
        return form_class(data, **kwargs)

    def get_form_class(self):
        return self.form_class

    def get_form_initial(self):
        return self.request.GET or {}


@login_protected()
class CallApiView(FormView):

    endpoint = None

    endpoint_method = 'post'

    expected_status = 200

    title = None

    def form_valid(self, form):
        data = form.cleaned_data
        endpoint = self.get_endpoint(data)
        response_status, response_data = call_api(
            self.request, self.endpoint_method, endpoint, data
        )
        if response_status == self.expected_status:
            self.send_messages()
            return redirect(self.request.path)

        context = self.get_context_data(
            form=form,
            response_status=response_status,
            response_data=response_data
        )
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.get_title()
        context.update({
            'name': title,
            'breadcrumblist': [(title, self.request.path)]
        })
        return context

    def get_endpoint(self, data):
        return self.endpoint

    def get_title(self):
        return self.title

    def send_messages(self):
        pass
