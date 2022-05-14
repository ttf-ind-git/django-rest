from django.urls import path, re_path, include
from emp import views
import emp
from emp import api_urls

urlpatterns = [
   
    #Home page
    path('', views.index, name='home'),
	path('home/', views.index, name='home'),

    path('api/v1/', include(emp.api_urls))


]