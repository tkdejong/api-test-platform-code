from rest_framework import serializers
from .models import CustomToken

class CustomTokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """

    class Meta:
        model = CustomToken
        fields = ('key',)
        abstract = True
