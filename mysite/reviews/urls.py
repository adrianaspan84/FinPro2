from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_list, name='reviews_list'),
    path('create/', views.ReviewCreateView.as_view(), name='reviews_create'),
    path('<int:review_id>/edit/', views.ReviewUpdateView.as_view(), name='reviews_edit'),
    path('<int:review_id>/delete/', views.ReviewDeleteView.as_view(), name='reviews_delete'),
]
