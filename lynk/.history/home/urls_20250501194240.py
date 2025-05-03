from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home_page'),
    path('select/delivery/', views.SelectDelivery.as_view(), name='select_delivery'),
    path('waiting/<int:request_id>/', views.WaitingForApproval.as_view(), name='waiting_for_approval'),
]