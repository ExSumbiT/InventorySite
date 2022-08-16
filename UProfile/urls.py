"""Test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from UProfile import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('<str:type_name>/<int:index>', views.type_index, name='type_index'),
    # path('<str:type_name>/<int:index>/delete', views.type_index_delete, name='type_index_delete'),
    # path('<str:type_name>', views.type_list, name='type_list'),
    # path('parameters/create', views.create_parameter, name='create_parameter'),
    # path('types/create', views.create_type, name='create_type'),
    # path('types/update/<str:type_name>', views.update_type, name='update_type'),
    path('qr/', views.qr, name='qr'),
    path('qr_range/<str:inv_type>/<str:index_from>/<str:index_to>', views.qr_range, name='qr_range'),
    path('qr_range_valid/', views.qr_range_valid, name='qr_range_valid'),
    # path('qr_generator/', views.qr_generator, name='qr_generator'),
    path('change_password/', views.change_password, name='change_password'),
    path('import/preview/', views.preview, name='preview'),
    path('import/', views.import_xlsx, name='import_xlsx'),
    path('', views.profile, name='profile'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
