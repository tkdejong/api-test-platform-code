import logging
import copy
import collections
from copy import deepcopy

from django import forms
from filer.models.filemodels import File
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from guardian.admin import AdminUserObjectPermissionsForm, AdminGroupObjectPermissionsForm
from django.forms.models import inlineformset_factory

from tinymce.widgets import TinyMCE

from .models import (
    ServerRun, Endpoint, TestScenario,
    Environment, ScheduledTestScenario, TestScenarioUrl, PostmanTest
)
from ..utils.newman import NewmanManager
from ..utils.forms import CustomModelChoiceField

logger = logging.getLogger(__name__)


class CreateServerRunForm(forms.ModelForm):

    # test_scenario = CustomModelChoiceField(TestScenario.objects.filter(active=True), widget=forms.RadioSelect, empty_label=None)

    class Meta:
        model = ServerRun
        fields = [
            'test_scenario',
        ]

    def __init__(self, *args, **kwargs):
        api_id = kwargs.pop('api_id', None)
        super().__init__(*args, **kwargs)
        if api_id:
            self.fields['test_scenario'] = CustomModelChoiceField(
                TestScenario.objects.filter(active=True, api=api_id),
                widget=forms.RadioSelect,
                empty_label=None
            )

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
        self.test_scenario = kwargs.pop('test_scenario', None)
        self.user = kwargs.pop('user', None)
        self.scheduled = kwargs.pop('scheduled', None)

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('environment') and not cleaned_data.get('create_env'):
            raise ValidationError(_("Please select either an environment or check create new environment"))

        qs = Environment.objects.filter(
            test_scenario=self.test_scenario,
            name=cleaned_data['create_env'],
            user=self.user
        )
        if qs.exists():
            raise ValidationError(_(
                "An environment with this name for this test scenario already exists, please choose "
                "a different name or select an existing environment."
            ))

        if self.scheduled and cleaned_data.get('environment'):
            qs = ScheduledTestScenario.objects.filter(
                test_scenario=self.test_scenario,
                environment=cleaned_data.get('environment'),
                user=self.user
            )
            if qs.exists():
                raise ValidationError(_(
                    "A schedule for this test scenario and environment already exists, please create "
                    "a new environment or select an existing environment."
                ))


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


class CreateTestScenarioUrlForm(forms.ModelForm):

    class Meta:
        model = TestScenarioUrl
        exclude = ()


TestScenarioUrlFormSet = inlineformset_factory(
    TestScenario,
    TestScenarioUrl,
    form=CreateTestScenarioUrlForm,
    can_delete=False,
    extra=0
)

TestScenarioUrlUpdateFormSet = inlineformset_factory(
    TestScenario,
    TestScenarioUrl,
    form=CreateTestScenarioUrlForm,
    can_delete=True,
    extra=0
)


class UploadPostmanTestForm(forms.ModelForm):

    validation_file = forms.FileField(required=True)

    class Meta:
        model = PostmanTest
        exclude = ()


PostmanTestFormSet = inlineformset_factory(
    TestScenario,
    PostmanTest,
    form=UploadPostmanTestForm,
    can_delete=False,
    extra=0
)

PostmanTestUpdateFormSet = inlineformset_factory(
    TestScenario,
    PostmanTest,
    form=UploadPostmanTestForm,
    can_delete=True,
    extra=0
)


class CreateTestScenarioForm(forms.ModelForm):

    description = forms.CharField(widget=TinyMCE())

    class Meta:
        model = TestScenario
        fields = ['name', 'description', 'public_logs', 'active']
        help_texts = {
            'name': ''
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if not self.instance:
            if TestScenario.objects.filter(name=name).exists():
                raise ValidationError(_(
                    "A test scenario with this name already exists"
                ))
        return name


class EnvironmentUpdateForm(forms.ModelForm):

    name = forms.CharField(required=False, help_text=_("The name of the environment"))

    class Meta:
        model = Environment
        fields = ['name']


class CustomPermissionChoicesMixin:
    def get_obj_perms_field_choices(self):
        """
        Show only the custom permissions as the available object permissions
        """
        choices = super().get_obj_perms_field_choices()
        permission_codes = [code for code, _ in self.obj._meta.permissions]
        choices = [(perm, label) for perm, label in choices if perm in permission_codes]
        return choices


class CustomAdminUserObjectPermissionsForm(CustomPermissionChoicesMixin, AdminUserObjectPermissionsForm):
    pass


class CustomAdminGroupObjectPermissionsForm(CustomPermissionChoicesMixin, AdminGroupObjectPermissionsForm):
    pass


class CollectionGeneratorForm(forms.Form):
    oas_file = forms.FileField(required=True, help_text=_(
        "A .yaml file containing an OpenAPI specification"
    ))
    filename = forms.CharField(required=True, help_text=_(
        "The name to be used for the generated Postman collection"
    ))
