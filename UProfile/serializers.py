from rest_framework import serializers
from UProfile.models import QrParameters

class QrParametersSerializer(serializers.ModelSerializer):
    class Meta:
        model = QrParameters
        fields = ('weight', 'height', 'font', 'font_size', 'description_logo', 'logo_size')