from inv.models import Inventory, InventoryType, Parameter
from .serializers import InventorySerializer
import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser


@csrf_exempt
def type_index(request, type_name, index):
    """
    Retrieve, update or delete a Inventory.
    """
    try:
        print(type_name, index)
        obj = Inventory.objects.filter(type__short_name=type_name, index=index).order_by('parameter__order')
        print(obj)
    except Inventory.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        data = []
        for _ in obj:
            data.append(json.dumps(InventorySerializer(_).data))
        return JsonResponse({'data': data})

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = InventorySerializer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        obj.delete()
        return HttpResponse(status=204)
