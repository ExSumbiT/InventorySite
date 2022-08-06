from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.conf import settings
from inv.models import Parameter, InventoryType
from inv.views import parse_xlsx
from django.core.files.storage import default_storage
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
import os
from .forms import ChangePasswordForm, LoginForm
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
import pyqrcode
from PIL import Image, ImageDraw, ImageFont
import textwrap
from zipfile import ZipFile
from django.contrib.auth.models import User


def profile(request):
    parameters = Parameter.objects.all()
    inventory_types = InventoryType.objects.all()
    return render(request, 'Profile.html', context={'parameters': parameters, 'inventory_types': inventory_types,
                                                    'change_password': ChangePasswordForm(request.user)})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(request.POST.get('next', '/'))
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
        else:
            print(form.errors)
            return HttpResponse('Invalid form')
    return HttpResponseRedirect(request.POST.get('next', '/'))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(request.POST.get('next', '/'))


def main(request):
    return render(request, 'Index.html')


@csrf_exempt
def preview(request):
    item_list = []
    if request.method == 'POST':
        file = request.FILES['file']
        xlsx = pd.ExcelFile(file)
        for sheet in xlsx.sheet_names:
            df = pd.read_excel(file, sheet_name=sheet, header=None)
            df.fillna(' ', inplace=True)
            for row in df.iterrows():
                item_list.append(row[1].values.tolist())
    return JsonResponse(item_list, safe=False)


def import_xlsx(request):
    if request.method == 'POST':
        file = request.FILES['xlsx']
        file_name = default_storage.save(file.name, file)
        f = default_storage.path(file_name)
        parse_xlsx(f)
        default_storage.delete(file_name)
    return render(request, 'Import.html')


def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, data=request.POST or None)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return JsonResponse({'status': ['Пароль поновлено!']})
        else:
            return JsonResponse({'errors': form.errors}, status=500)
    return HttpResponseRedirect(request.POST.get('next', '/'))


def qr_create(inv_type: str, ind: str, url: str):
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, f'qr-code/{inv_type}')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, f'qr-code/{inv_type}'))
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, f'temp')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, f'temp'))
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, f'qr-code/{inv_type}/qr_{ind}.png')):
        return f'qr-code/{inv_type}/qr_{ind}.png'
    w = 30  # 100 pixels wide
    h = 50  # 100 pixels high
    img = Image.new('RGB', (w, h), color='#FFFFFF')
    canvas = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.join(settings.STATIC_ROOT, 'fonts/arial.ttf'), size=14)
    lines = textwrap.wrap(f'{inv_type}{ind}', width=len(inv_type))
    y_text = 0
    for line in lines:
        width, height = font.getsize(line)
        canvas.text(((w - width) / 2, y_text), line, font=font, fill='#000000')
        y_text += height * 3 / 2
    img.save(os.path.join(settings.MEDIA_ROOT, 'temp/logo.png'), "PNG")
    # Generate the qr code and save as png
    qrobj = pyqrcode.QRCode(url, error='H')
    qrobj.png(os.path.join(settings.MEDIA_ROOT, f'temp/qr_{inv_type}{ind}.png'), scale=3)
    # Now open that png image to put the logo
    img = Image.open(os.path.join(settings.MEDIA_ROOT, f'temp/qr_{inv_type}{ind}.png'))
    width, height = img.size
    # How big the logo we want to put in the qr code png
    logo_size = 30
    # Open the logo image
    logo = Image.open(os.path.join(settings.MEDIA_ROOT, 'temp/logo.png'))
    img = img.convert("RGBA")
    # Calculate xmin, ymin, xmax, ymax to put the logo
    xmin = ymin = int((width / 2) - (logo_size / 2))
    xmax = ymax = int((width / 2) + (logo_size / 2))
    # resize the logo as calculated
    logo = logo.resize((xmax - xmin, ymax - ymin))
    # put the logo in the qr code
    img.paste(logo, (xmin, ymin, xmax, ymax))
    img.save(os.path.join(settings.MEDIA_ROOT, f'qr-code/{inv_type}/qr_{ind}.png'))
    os.remove(os.path.join(settings.MEDIA_ROOT, 'temp/logo.png'))
    os.remove(os.path.join(settings.MEDIA_ROOT, f'temp/qr_{inv_type}{ind}.png'))
    return f'qr-code/{inv_type}/qr_{ind}.png'


def qr_range(request):
    inv_type = request.POST['inv_type']
    index_from = request.POST['index_from']
    index_to = request.POST['index_to']
    zip_obj = ZipFile(os.path.join(settings.MEDIA_ROOT, f'{inv_type}_{index_from}-{index_to}.zip'), 'w')
    for ind in range(int(index_from), int(index_to)+1):
        ind = str(ind)
        img = qr_create(inv_type, ind, request.build_absolute_uri(f'/inv/{inv_type}/{ind}'))
        zip_obj.write(os.path.join(settings.MEDIA_ROOT, img), img.split('/')[-1])
    zip_obj.close()
    with open(os.path.join(settings.MEDIA_ROOT, f'{inv_type}_{index_from}-{index_to}.zip'), 'rb') as dw:
        response = HttpResponse(dw.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = f'inline; filename={inv_type}_{index_from}-{index_to}.zip'
    os.remove(os.path.join(settings.MEDIA_ROOT, f'{inv_type}_{index_from}-{index_to}.zip'))
    return response


def qr(request):
    print(request.build_absolute_uri('/'))
    inv_type = request.POST['inv_type']
    ind = request.POST['index']
    img = qr_create(inv_type, ind, request.build_absolute_uri(f'/inv/{inv_type}/{ind}'))
    return HttpResponseRedirect(f'/static/{img}')
