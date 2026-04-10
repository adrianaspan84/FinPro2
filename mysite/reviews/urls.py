from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_list, name='reviews_list'),
    path('create/', views.review_create, name='reviews_create'),
    path('<int:review_id>/edit/', views.review_edit, name='reviews_edit'),
    path('<int:review_id>/delete/', views.review_delete, name='reviews_delete'),
]
