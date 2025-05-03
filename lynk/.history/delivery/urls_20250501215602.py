from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('', views.DeliveryHome.as_view(), name='delivery_home'),
    path('accept/<int:request_id>/', views.AcceptDeliveryRequest.as_view(), name='accept_request'),
    path('reject/<int:request_id>/', views.RejectDeliveryRequest.as_view(), name='reject_request'),
    path('active/', views.ActiveDeliveries.as_view(), name='active_deliveries'),
    path('status/<int:request_id>/', views.CheckRequestStatus.as_view(), name='check_status'),
    path('accepted-confirmation/', views.DeliveryAcceptedConfirmation.as_view(), name='delivery_accepted_confirmation'),
]