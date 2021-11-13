from django.db.models.query import QuerySet
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import generics
from .serializers import *
from authorization.models import Machine, CustomUser
from .models import MachineContainers
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import status
from rest_framework.exceptions import APIException
# TODO When user likes own recipe like goes to orginal one
# TODO Tea portion dynamicly


def filter_recipes(params: dict, queryset: QuerySet):
    """
    List public recipes. List of query parameters
    name - name of recipe
    tea_type
    ingredient_1
    ingredient_2
    ingredient_3
    brewing_temperature_down
    brewing_temperature_up
    brewing_time_down
    brewing_time_up
    mixing_time_down
    mixing_time_up
    """
    for param in params:
        if param == "name":
            queryset = queryset.filter(recipe_name__iregex=f".*(?={params[param]}).*")
            continue
        if param == "tea_type":
            queryset = queryset.filter(tea_type__tea_name=params[param])
            continue
        if "ingredient" in param:
            queryset = queryset.filter(
                ingredientsrecipes__ingredient__ingredient_name=params[param]
            )
            continue
        if param == "brewing_temperature_down":
            queryset = queryset.filter(brewing_temperature__gte=params[param])
            continue
        if param == "brewing_temperature_up":
            queryset = queryset.filter(brewing_temperature__lte=params[param])
            continue
        if param == "brewing_time_down":
            queryset = queryset.filter(brewing_time__gte=params[param])
            continue
        if param == "brewing_time_up":
            queryset = queryset.filter(brewing_time__lte=params[param])
            continue
        if param == "mixing_time_down":
            queryset = queryset.filter(mixing_time__gte=params[param])
            continue
        if param == "mixing_time_up":
            queryset = queryset.filter(mixing_time__lte=params[param])
            continue
    return queryset

class WrongQuerystringValue(APIException):
    status_code = 422
    default_detail = "Invalid query string. Value must be numeric type."
    default_code = "wrong_query_string"

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            obj.customuser_set.get(pk=request.user.id)
            return True
        except CustomUser.DoesNotExist:
            if request.user.is_superuser:
                return True
            return False


class IsAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        if obj.author == request.user:
            return True
        if request.user.is_superuser:
            return True
        return False


class GetMachineInfo(APIView):
    """
    Get specific machine info
    """

    permission_classes = [
        IsOwnerOrAdmin,
    ]

    def get(self, request, pk, format=None):
        queryset = Machine.objects.all()
        machine = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, machine)
        serializer = MachineInfoSerializer(machine)
        return Response(serializer.data)

class ListMachines(generics.ListAPIView):
    """
    List all machines
    """

    queryset = Machine.objects.all()
    serializer_class = MachineInfoSerializer
    permission_classes = [permissions.IsAdminUser]


class GetMachineContainers(generics.ListAPIView):
    """
    Get info about machine containers. Pass machine id in URL
    """

    permission_classes = [
        IsOwnerOrAdmin,
    ]
    serializer_class = MachineContainersSerializer
    queryset = MachineContainers.objects.all()

    def list(self, request, pk):
        machine = Machine.objects.all()
        self.check_object_permissions(request, get_object_or_404(machine, pk=pk))
        queryset = MachineContainers.objects.filter(machine__pk=pk)
        serializer = MachineContainersSerializer(queryset, many=True)
        return Response(serializer.data)


class ListPublicRecipes(generics.ListAPIView):
    """
    List public recipes with filters
    """

    serializer_class = RecipesSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Recipes.objects.filter(is_public=True)

    def get_queryset(self):
        try:
            return filter_recipes(
                self.request.query_params, Recipes.objects.filter(is_public=True)
            )
        except ValueError:
            raise WrongQuerystringValue()


class UserRecipes(viewsets.ModelViewSet):
    """
    Used to do all staff with logged user recipes. Doesnt have access to other recipes
    """

    permission_classes_by_action = {
        "update": [IsAuthorOrAdmin],
        "partial_update": [IsAuthorOrAdmin],
        "destroy": [IsAuthorOrAdmin],
        "create": [permissions.IsAuthenticated],
        "list": [permissions.IsAuthenticated],
        "retrieve": [IsAuthorOrAdmin],
    }
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except KeyError:
            # action is not set return default permission_classes
            return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = Recipes.objects.filter(author=request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    """
    def get_queryset(self):
        user = self.request.user
        return Recipes.objects.filter(is_public=True)
    """
