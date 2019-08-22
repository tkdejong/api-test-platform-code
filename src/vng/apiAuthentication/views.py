from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import FormView
from .models import CustomToken
from .serializers import CustomTokenSerializer

from rest_auth.views import LoginView, LogoutView

from .forms import TokenForm

class CustomLoginView(LoginView):
    token_model = CustomToken

    def get_response_serializer(self):
        return CustomTokenSerializer


class CustomLogoutView(LogoutView):
    token_model = CustomToken

    def get_response_serializer(self):
        return CustomTokenSerializer


class TokenManager(LoginRequiredMixin, FormView):

    template_name = 'apiAuthentication/token_manager.html'
    form_class = TokenForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tokens'] = CustomToken.objects.filter(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        user = request.user

        if 'delete_items' in request.POST:
            pk = int(request.POST['delete_items'])
            token = CustomToken.objects.get(pk=pk)
            token.delete()

        if 'generate_new' in request.POST:
            form = self.form_class(request.POST, user=user)
            if form.is_valid():
                token = form.save(commit=False)
                token.user = user
                token.save()
            else:
                context = self.get_context_data()
                context['form'] = form
                return render(request, 'apiAuthentication/token_manager.html', context=context)

        return redirect(reverse('apiv1_auth:token-manager'))
