from django import forms

from .models import DesignRuleSession


class DesignRulesSessionForm(forms.ModelForm):
    class Meta:
        model = DesignRuleSession
        fields = ("api_endpoint", )
