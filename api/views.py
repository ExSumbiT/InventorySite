from inv.models import Inventory, InventoryType, Parameter
from .serializers import InventorySerializer
import json

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

# TODO: додати підтримку сповіщень при поверненні з функції
@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def type_index(request, type_name, index):
    """
    Retrieve, update or delete a Inventory.
    """
    try:
        obj = Inventory.objects.filter(type__short_name=type_name, index=index).order_by('parameter__order')
    except Inventory.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        data = []
        for _ in obj:
            data.append(json.dumps(InventorySerializer(_).data))
        return JsonResponse({'data': data})

    elif request.method == 'PUT':
        for k, v in request.data.items():
            _ = obj.filter(parameter__type=k).first()
            serializer = InventorySerializer(_, data={'value': v, 'index': index})
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)
                return JsonResponse(serializer.errors, status=400)
        return JsonResponse({'status': 'ok'})

    elif request.method == 'DELETE':
        for _ in obj:
            _.delete()
        return HttpResponse(status=204)
