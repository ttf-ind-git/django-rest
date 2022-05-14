from xml.etree.ElementInclude import include
from django.urls import path, include
from emp.views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register('', EmployeeViewset)


urlpatterns = [
    

    # function based views
    path('emp_all/', emp_all),
    path('emp_details/<int:id>/', emp_details),

    # viewset
    path('employee/', include(router.urls)),

    # class based views (ApiView)
    path('emp_all_class/', EmpAPIView.as_view()),
    path('emp_details_class/<int:id>/', EmpDetailView.as_view()),

    # using GenericAPIView mixins(GenericView)
    path('generics/emp/', EmpListView.as_view()),
    path('generics/emp/<int:id>/', EmpListView.as_view()),

    # using generic ListApiView - to implementing filter
    path('generic/EmpListView/', EmployeeListView.as_view()),

    # login & logout
    path('auth/login/', LoginView.as_view()),
    path('auth/logout/', LogoutView.as_view())


]