from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
from inv.models import Parameter, Inventory, InventoryType
import pandas as pd


def create_inventory(inv_type, parameters, values, index):
    for i, parameter in enumerate(parameters):
        Inventory.objects.create(parameter=parameter, type=inv_type, value=values[i], index=index)


def update_inventory(inv_type, parameters, values, index):
    for i, parameter in enumerate(parameters):
        Inventory.objects.filter(type=inv_type, index=index, parameter=parameter).update(value=values[i])


def type_index(request, type_name, index):
    type_parameters = InventoryType.objects.filter(short_name=type_name)[0].parameters.all()
    if request.method == 'POST':
        values = []
        print(request.POST)
        for parameter in type_parameters:
            values.append(request.POST[parameter.type])
        if Inventory.objects.filter(type__short_name=type_name, index=index).count() > 0:
            update_inventory(InventoryType.objects.filter(short_name=type_name)[0], type_parameters, values, str(index))
            return redirect('type_index', type_name=type_name, index=index)
        else:
            create_inventory(InventoryType.objects.filter(short_name=type_name)[0], type_parameters, values, str(index))
        return HttpResponse('ok')
    else:
        if Inventory.objects.filter(type__short_name=type_name, index=index).count() > 0:
            values = {}
            for parameter in type_parameters:
                obj = Inventory.objects.filter(parameter=parameter, type__short_name=type_name, index=index)[0]
                if obj.parameter.html_type == 'date':
                    values[obj.parameter] = obj.value.split(' ')[0]
                else:
                    values[obj.parameter] = obj.value
            return render(request, 'InventoryIndex.html', context={'short_name': type_name, 'index': index,
                                                                   'values': values.items()})
        return render(request, 'Inventory.html', context={'short_name': type_name, 'index': index,
                                                          'parameters': type_parameters})


def type_index_delete(request, type_name, index):
    if request.user.is_superuser:
        inv_objs = Inventory.objects.filter(type__short_name=type_name, index=index)
        if inv_objs.count() > 0:
            for inv_obj in inv_objs:
                inv_obj.delete()
        return redirect('type_list', type_name=type_name)
    return HttpResponse('Not Permitted')


def type_list(request, type_name):
    values = {}
    parameters = []
    for index in Inventory.objects.filter(type__short_name=type_name).values('index').distinct():
        index = index['index']
        values[index] = []
        for parameter in InventoryType.objects.filter(short_name=type_name)[0].parameters.all():
            obj = Inventory.objects.filter(parameter=parameter, type__short_name=type_name, index=index)[0]
            if obj.parameter.show:
                if obj.parameter.name not in parameters:
                    parameters.append(obj.parameter.name)
                if obj.parameter.html_type == 'date':
                    values[index].append(obj.value.split(' ')[0])
                else:
                    values[index].append(obj.value)
    return render(request, 'Types.html', context={'parameters': parameters, 'values': values.items(),
                                                  'deep': True, 'type_name': type_name})


def types(request):
    type_obj_list = InventoryType.objects.all()
    values = [[t.short_name, t.full_name,
               Inventory.objects.all().filter(type=t).values('index').distinct().count()] for t in type_obj_list]
    return render(request, 'Types.html', context={'values': values, 'deep': False})


def create_type(request):
    parameters = Parameter.objects.all()
    if request.method == 'POST':
        type_parameters = [Parameter.objects.filter(name=name)[0] for name in request.POST.getlist('parameters')]
        InventoryType.objects.create(full_name=request.POST['full_name'],
                                     short_name=request.POST['short_name']).parameters.set(type_parameters)
        return HttpResponse('ok')
    else:
        return render(request, 'InventoryTypeCreate.html', context={'parameters': parameters})


# def update_type(request, type_name):
#     if request.user.is_superuser:
#         type_obj = InventoryType.objects.filter(short_name=type_name)[0]
#         checked_parameters = [Parameter.objects.filter(id=_)[0] for _ in request.POST.getlist('parameters')]
#         for type_parameter in type_obj.parameters.all():
#             if type_parameter not in checked_parameters:
#                 type_obj.parameters.remove(type_parameter)
#                 for inv in Inventory.objects.filter(type=type_obj).all():
#                     if Inventory.objects.filter(type=type_obj, parameter=type_parameter, index=inv.index).count() > 0:
#                         Inventory.objects.filter(parameter=type_parameter, type=type_obj, index=inv.index).delete()
#         for parameter in checked_parameters:
#             if parameter not in type_obj.parameters.all():
#                 type_obj.parameters.add(parameter)
#                 for inv in Inventory.objects.filter(type=type_obj).all():
#                     if not Inventory.objects.filter(type=type_obj, parameter=parameter, index=inv.index).count() > 0:
#                         Inventory.objects.create(parameter=parameter, type=type_obj, value='null', index=inv.index)
#         return HttpResponseRedirect(request.POST.get('next', '/'))
#     return HttpResponse('Not Permitted')


def about_type(request, type_name):
    if request.user.is_superuser:
        if request.method == 'POST':
            type_obj = InventoryType.objects.filter(short_name=type_name)[0]
            checked_parameters = [Parameter.objects.filter(id=_)[0] for _ in request.POST.getlist('parameters')]
            for type_parameter in type_obj.parameters.all():
                if type_parameter not in checked_parameters:
                    type_obj.parameters.remove(type_parameter)
                    for inv in Inventory.objects.filter(type=type_obj).all():
                        if Inventory.objects.filter(type=type_obj, parameter=type_parameter,
                                                    index=inv.index).count() > 0:
                            Inventory.objects.filter(parameter=type_parameter, type=type_obj, index=inv.index).delete()
            for parameter in checked_parameters:
                if parameter not in type_obj.parameters.all():
                    type_obj.parameters.add(parameter)
                    for inv in Inventory.objects.filter(type=type_obj).all():
                        if not Inventory.objects.filter(type=type_obj, parameter=parameter,
                                                        index=inv.index).count() > 0:
                            Inventory.objects.create(parameter=parameter, type=type_obj, value='null', index=inv.index)
            return HttpResponseRedirect(request.POST.get('next', '/'))
        type_obj = InventoryType.objects.filter(short_name=type_name)[0]
        parameters = Parameter.objects.all()
        return render(request, 'InventoryTypeAbout.html', context={'parameters': parameters, 'type_obj': type_obj})
    return HttpResponse('Not Permitted')


def create_parameter(request):
    html_types = ['text', 'date']
    parameters = Parameter.objects.all()
    if request.method == 'POST':
        Parameter.objects.create(name=request.POST['name'], type=request.POST['type'],
                                 html_type=request.POST['html_type'])
        return HttpResponse('ok')
    else:
        return render(request, 'ParameterCreate.html', context={'parameters': parameters,
                                                                'html_types': html_types})


def parse_xlsx(filename: str):
    xlsx = pd.ExcelFile(filename)
    for sheet in xlsx.sheet_names:
        df = pd.read_excel(filename, sheet_name=sheet, header=None)
        for row in df.iterrows():
            items = row[1].values.tolist()
            type_obj = InventoryType.objects.filter(short_name=items[0])[0]
            try:
                index = Inventory.objects.filter(type=type_obj).latest('index').index
            except:
                index = 0
            create_inventory(type_obj, type_obj.parameters.all(), items[1:], str(int(index)+1))
    xlsx.close()

