from django.urls import path
from . import views

urlpatterns = [
    path('', views.horse_list, name='horse_list'),
    path('cheval/ajouter/', views.horse_add, name='horse_add'),
    path('cheval/<int:pk>/', views.horse_detail, name='horse_detail'),
    path('cheval/<int:horse_pk>/entrainement/ajouter/', views.training_add, name='training_add'),
]