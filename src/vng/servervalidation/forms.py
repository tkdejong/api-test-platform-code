import logging
import copy
import collections
from copy import deepcopy

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import ServerRun, Endpoint, TestScenario, Environment
from ..utils.newman import NewmanManager
from ..utils.forms import CustomModelChoiceField

logger = logging.getLogger(__name__)


class CreateServerRunForm(forms.ModelForm):

    test_scenario = CustomModelChoiceField(TestScenario.objects.filter(active=True), widget=forms.RadioSelect, empty_label=None)

    class Meta:
        model = ServerRun
        fields = [
            'test_scenario',
            'scheduled',
        ]

    def clean(self):
        """
        Tries to process the test scenario json to make sure the input is valid.
        """
        test_scenario = self.cleaned_data.get('test_scenario')


class SelectEnvironmentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        envs = kwargs.pop('envs', None)
        if envs:
            self.fields['environment'] = forms.ModelChoiceField(envs, required=False)
        self.fields['create_env'] = forms.CharField(label=_('Create new environment'), required=False)

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('environment') and not cleaned_data.get('create_env'):
            raise ValidationError(_("Please select either an environment or check create new environment"))
        return cleaned_data


class CreateEndpointForm(forms.Form):

    def set_labels(self, labels):
        tmp = collections.OrderedDict()
        for k, new in zip(self.fields.keys(), labels):
            self.fields[k].label = new

    def add_text_area(self, text_area):
        for e in text_area:
            self.fields[e] = forms.CharField(widget=forms.Textarea)

    def __init__(self,
                 url_vars=None,
                 text_vars=None,
                 url_placeholders=None,
                 text_placeholders=None,
                 *args,
                 **kwargs):
        super().__init__(*args)

        if url_vars:
            if not url_placeholders:
                url_placeholders = ['http://www.example.com' for i in range(len(url_vars))]

            for url_var, placeholder in zip(url_vars, url_placeholders):
                self.fields[url_var.name] = forms.URLField(
                    widget=forms.URLInput(attrs={'placeholder': placeholder}),
                    initial=placeholder
                )

        if text_vars:
            if not text_placeholders:
                text_placeholders = ['text' for i in range(len(text_vars))]

            for text_var, placeholder in zip(text_vars, text_placeholders):
                self.fields[text_var.name] = forms.CharField(
                    widget=forms.Textarea(),
                    initial=placeholder
                )
