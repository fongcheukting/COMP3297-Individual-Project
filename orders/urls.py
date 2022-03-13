from django.urls import path
from orders import views

urlpatterns = [
path('hello', views.hello),
path('view_all', views.view_all),
path('QDD', views.QDD),
path(r'^$', views)
]