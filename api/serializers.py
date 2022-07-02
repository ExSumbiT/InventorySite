from rest_framework import serializers
from inv.models import Inventory, InventoryType, Parameter


class InventoryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryType
        fields = ('full_name', 'short_name')


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('name', 'type', 'html_type', 'order', 'show')


class InventorySerializer(serializers.ModelSerializer):
    parameter = ParameterSerializer(read_only=True)
    type = InventoryTypeSerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = ('type', 'index', 'parameter', 'value', 'date')
        depth = 1
