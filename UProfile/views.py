from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.conf import settings
from inv.models import Parameter
from inv.views import parse_xlsx
from django.core.files.storage import default_storage
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
import os
import pyqrcode
from PIL import Image, ImageDraw, ImageFont
import textwrap
from django.contrib.auth.models import User


def profile(request):
    parameters = Parameter.objects.all()
    return render(request, 'Profile.html', context={'parameters': parameters})


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
        new_password = request.POST['new_password']
        if new_password == request.POST['confirm_password']:
            user = request.user
            user.set_password(new_password)
            user.save()
        else:
            return HttpResponse('check password')
    return HttpResponseRedirect(request.POST.get('next', '/'))


def qr_create(inv_type: str, ind: str, url: str):
    if os.path.exists(os.path.join(settings.STATIC_ROOT, f'qr-code/{inv_type}/qr_{ind}.png')):
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
    img.save(os.path.join(settings.STATIC_ROOT, 'temp/logo.png'), "PNG")
    # Generate the qr code and save as png
    qrobj = pyqrcode.QRCode(url, error='H')
    qrobj.png(os.path.join(settings.STATIC_ROOT, f'temp/qr_{inv_type}{ind}.png'), scale=3)
    # Now open that png image to put the logo
    img = Image.open(os.path.join(settings.STATIC_ROOT, f'temp/qr_{inv_type}{ind}.png'))
    width, height = img.size
    # How big the logo we want to put in the qr code png
    logo_size = 30
    # Open the logo image
    logo = Image.open(os.path.join(settings.STATIC_ROOT, 'temp/logo.png'))
    img = img.convert("RGBA")
    # Calculate xmin, ymin, xmax, ymax to put the logo
    xmin = ymin = int((width / 2) - (logo_size / 2))
    xmax = ymax = int((width / 2) + (logo_size / 2))
    # resize the logo as calculated
    logo = logo.resize((xmax - xmin, ymax - ymin))
    # put the logo in the qr code
    img.paste(logo, (xmin, ymin, xmax, ymax))
    img.save(os.path.join(settings.STATIC_ROOT, f'qr-code/{inv_type}/qr_{ind}.png'))
    os.remove(os.path.join(settings.STATIC_ROOT, 'temp/logo.png'))
    os.remove(os.path.join(settings.STATIC_ROOT, f'temp/qr_{inv_type}{ind}.png'))
    return f'qr-code/{inv_type}/qr_{ind}.png'


def qr_range(request):
    pass


def qr(request):
    inv_type = request.POST['inv_type']
    ind = request.POST['index']
    img = qr_create(inv_type, ind, request.build_absolute_uri())
    return HttpResponseRedirect(f'/static/{img}')
