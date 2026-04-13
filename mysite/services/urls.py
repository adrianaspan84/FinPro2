from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.services_home, name='services_home'),

    # ServiceCategory CRUD
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Service CRUD
    path('manage/', views.service_list, name='service_list'),
    path('manage/create/', views.service_create, name='service_create'),
    path('manage/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('manage/<int:pk>/delete/', views.service_delete, name='service_delete'),
]
