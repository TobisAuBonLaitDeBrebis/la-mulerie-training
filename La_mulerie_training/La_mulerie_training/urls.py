"""
URL configuration for La_mulerie_training project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from training import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.horse_list, name='horse_list'),
    path('cheval/ajouter/', views.horse_add, name='horse_add'),
    path('cheval/<int:pk>/', views.horse_detail, name='horse_detail'),
    path('cheval/<int:horse_pk>/entrainement/ajouter/', views.training_add, name='training_add'),
]
