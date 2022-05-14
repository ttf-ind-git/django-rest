from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User

from emp import serializers
from emp.serializers import EmployeeSerializer
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from rest_framework import generics
from rest_framework import mixins

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .serializers import LoginSerializer
from django.contrib.auth import login as django_login, logout as django_logout
from rest_framework.authtoken.models import Token

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import FilterSet
from django_filters import rest_framework as filters

# Create your views here.

def index(request):
    return HttpResponse('API RESPONSE')


# login and logout

class LoginView(APIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        django_login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=200)


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication, )

    def post(self, request):
        django_logout(request)
        return Response(status=204)

# End login and logout


# ViewSets start

class EmployeeViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = EmployeeSerializer

# End Viewsets


# GenericAPIView with mixins start

class EmpListView(generics.GenericAPIView,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin):

    serializer_class = EmployeeSerializer
    queryset = User.objects.all()
    lookup_field = 'id'
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]



    def get(self, request, id=None):
        if id:
            return self.retrieve(request, id)
        else:
            return self.list(request)

    def post(self, request):
        return self.create(request)

    # def perform_create(self, serializer):
    #     serializer.save(created_by=self.request.user)

    def put(self, request, id=None):
        return self.update(request, id)

    # def perform_update(self, serializer):
    #     print(self.request.user)
    #     serializer.save(created_by=self.request.user)        

    def delete(self, request, id=None):
        return self.destroy(request, id)

# End GenericAPIView mixins

# User Defined filter start

class EmployeeFilter(FilterSet):
    is_active = filters.CharFilter('is_active')
    username = filters.CharFilter('username')

    class Meta:
        model = User
        fields = ('is_active', 'username',)

# End User Defined filter 


# generics ListAPIView start
# keyword to be use - ?is_active=True , ordering=username, ordering=-username, search=Admin

class EmployeeListView(generics.ListAPIView):
    serializer_class = EmployeeSerializer
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    # Default filter provided by Django
    # filter_fields = ('is_active', )

    # User defined filter
    filter_class = EmployeeFilter

    ordering_fields = ('is_active', 'username')
    ordering = ('username',)
    search_fields = ('username', 'first_name')


    # def get_queryset(self):
    #     queryset = User.objects.all()
    #     active = self.request.query_params.get('is_active', '')
    #     if active:
    #         if active == "False":
    #             active = False
    #         elif active == "True":
    #             active = True
    #         else:
    #             return queryset
    #         return queryset.filter(is_active=active)
    #     return queryset

# End generics ListAPIView 


# Fucntion based view start

@csrf_exempt
def emp_all(request):
    if request.method == "GET":
        questions = User.objects.all()
        serailizer = EmployeeSerializer(questions, many=True)
        return JsonResponse(serailizer.data, safe=False)

    elif request.method == "POST":
        json_parser = JSONParser()
        data = json_parser.parse(request)
        serializer = EmployeeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.erros, status=400)


@csrf_exempt
def emp_details(request, id):
    try:
        instance = User.objects.get(id=id)
    except User.DoesNotExist as e:
        return JsonResponse( {"error": "Given question object not found."}, status=404)

    if request.method == "GET":
        serailizer = EmployeeSerializer(instance)
        return JsonResponse(serailizer.data)

    elif request.method == "PUT":
        json_parser = JSONParser()
        data = json_parser.parse(request)
        serializer = EmployeeSerializer(instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.erros, status=400)

    elif request.method == "DELETE":
        instance.delete()
        return HttpResponse(status=204)

# End function based view


# ApiView

class EmpAPIView(APIView):
    def get(self, request):
        questions = User.objects.all()
        serailizer = EmployeeSerializer(questions, many=True)
        return Response(serailizer.data, status=200)

    def post(self, request):
        data = request.data
        serializer = EmployeeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.erros, status=400)

class EmpDetailView(APIView):
    def get_object(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist as e:
            return Response( {"error": "Given question object not found."}, status=404)

    def get(self, request, id=None):
        instance = self.get_object(id)
        serailizer = EmployeeSerializer(instance)
        return Response(serailizer.data)

    def put(self, request, id=None):
        data = request.data
        instance = self.get_object(id)
        serializer = EmployeeSerializer(instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.erros, status=400)

    def delete(self, request, id=None):
        instance = self.get_object(id)
        instance.delete()
        return HttpResponse(status=204)

# End ApiView