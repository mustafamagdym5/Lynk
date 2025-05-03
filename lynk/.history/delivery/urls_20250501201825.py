from django.urls import path
from .views import *

app_name = 'delivery'

urlpatterns = [
    path('', DeliveryHome.as_view(), name='delivery_home'),
    path('accept/<int:request_id>/', AcceptDeliveryRequest.as_view(), name='accept_request'),
    path('reject/<int:request_id>/', RejectDeliveryRequest.as_view(), name='reject_request'),
    path('active/', ActiveDeliveries.as_view(), name='active_deliveries'),
    path('request/<int:request_id>/status/', CheckRequestStatus.as_view(), name='check_status'),
    path('request/<int:request_id>/status/', views.CheckRequestStatus.as_view(), name='check_status'),
]