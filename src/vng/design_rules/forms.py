from django import forms

from .models import DesignRuleTestSuite


class DesignRuleTestSuiteForm(forms.ModelForm):
    class Meta:
        model = DesignRuleTestSuite
        fields = ("api_endpoint", )
