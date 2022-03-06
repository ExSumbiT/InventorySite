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
from inv import views

urlpatterns = [
    path('<str:type_name>/<int:index>', views.type_index, name='type_index'),
    path('<str:type_name>/<int:index>/delete', views.type_index_delete, name='type_index_delete'),
    path('<str:type_name>', views.type_list, name='type_list'),
    path('parameters/create', views.create_parameter, name='create_parameter'),
    path('types/create', views.create_type, name='create_type'),
    # path('types/update/<str:type_name>', views.update_type, name='update_type'),
    path('types/<str:type_name>', views.about_type, name='about_type'),
    path('', views.types, name='types'),
]
