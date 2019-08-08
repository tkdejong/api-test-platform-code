from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import FormView
from rest_framework.authtoken.models import Token


class TokenManager(LoginRequiredMixin, FormView):

    template_name = 'apiAuthentication/token_manager.html'
    form_class = Form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = Token.objects.filter(user=self.request.user).first()
        return context

    def post(self, request, *args, **kwargs):
        user = request.user

        token = Token.objects.filter(user=user).first()
        if token:
            token.delete()

        if 'generate_new' in request.POST:
            Token.objects.create(user=user)

        return redirect(reverse('apiv1_auth:token-manager'))
