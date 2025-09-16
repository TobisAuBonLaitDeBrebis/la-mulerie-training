from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cheval/ajouter/', views.horse_add, name='horse_add'),
    path('cheval/<int:pk>/', views.horse_detail, name='horse_detail'),
    path('cheval/<int:pk>/supprimer/', views.horse_delete, name='horse_delete'),
    path('cheval/<int:horse_pk>/entrainement/ajouter/', views.training_add, name='training_add'),
    path('entrainement/ajouter/', views.training_add, name='training_add_global'),
    path('entrainement/<int:pk>/supprimer/', views.training_delete, name='training_delete'),
]