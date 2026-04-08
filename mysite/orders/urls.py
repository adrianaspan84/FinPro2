from django.urls import path
from . import views

urlpatterns = [

    # CREATE + LIST
    path('create/', views.create_order, name='create_order'),
    path('list/', views.order_list, name='order_list'),

    # DASHBOARDS
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('client/', views.client_dashboard, name='client_dashboard'),

    # AJAX
    path('load-services/', views.load_services, name='load_services'),

    # STATUS CHANGE (TRŪKO!)
    path('<int:order_id>/status/<str:new_status>/',
         views.order_change_status,
         name='order_change_status'),

    # EDIT
    path('<int:order_id>/edit/', views.edit_order, name='edit_order'),

    # PDF
    path('invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),

    # DETAIL (VISADA PASKUTINIS!)
    path('<int:order_id>/', views.order_detail, name='order_detail'),
]
