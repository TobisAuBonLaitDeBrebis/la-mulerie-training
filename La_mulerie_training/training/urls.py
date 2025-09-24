from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_training, name='home_training'),
    path('cheval/home', views.home_horses, name='home_horses'),
    path('cheval/ajouter/', views.horse_add, name='horse_add'),
    path('cheval/<int:pk>/', views.horse_detail, name='horse_detail'),
    path('cheval/<int:pk>/edit', views.horse_edit, name='horse_edit'),
    path('cheval/<int:pk>/supprimer/', views.horse_delete, name='horse_delete'),

    path('cheval/<int:horse_pk>/entrainement/ajouter/', views.training_add, name='training_add'),
    path('entrainement/ajouter/', views.training_add, name='training_add_global'),
    # Edition
    path('entrainement/<int:pk>/edit/', views.training_edit, name='training_edit'),


    path('entrainement/<int:pk>/supprimer/', views.training_delete, name='training_delete'),
    path('entrainement/<int:pk>/details/', views.training_detail, name='training_detail'),

]