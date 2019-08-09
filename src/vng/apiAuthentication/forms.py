from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import ValidationError

from .models import CustomToken

class TokenForm(forms.ModelForm):

    class Meta:
        model = CustomToken
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        super(TokenForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if CustomToken.objects.filter(name=self.data['name'], user=self.user).exists():
            raise ValidationError(_("A token with this name already exists for this user"))
        return name
