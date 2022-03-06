from django.contrib import admin
from .models import Parameter, InventoryType, Inventory


admin.site.register(Parameter)
admin.site.register(InventoryType)
admin.site.register(Inventory)
