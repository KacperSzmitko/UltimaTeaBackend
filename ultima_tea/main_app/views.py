from django.db.models.query import QuerySet
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import generics, mixins, pagination
from authorization.models import Machine, CustomUser
from rest_framework import viewsets
from rest_framework.exceptions import APIException, ValidationError
from django.db.models import Q
from .models import *
from .tasks import *
from .serializers import *

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
        except AttributeError:
            try:
                obj.machine.customuser_set.get(pk=request.user.id)
                return True
            except CustomUser.DoesNotExist:
                if request.user.is_superuser:
                    return True
            except AttributeError:
                if obj.recipe.author.id == request.user.id:
                    return True
                return False
            return False


class IsAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        if obj.author == request.user:
            return True
        if request.user.is_superuser:
            return True
        return False


class MachineInfoViewSet(generics.ListAPIView):
    """
    List all user machines info
    """

    serializer_class = MachineInfoSerializer
    permission_classes = [IsOwnerOrAdmin]
    queryset = Machine.objects.all()

    def get_queryset(self):
        return Machine.objects.filter(customuser=self.request.user)


class UpdateTeaContainersView(generics.UpdateAPIView):
    """
    List or edit tea containers
    """

    serializer_class = UpdateTeasConatainerSerializer
    permission_classes = [IsOwnerOrAdmin]
    queryset = MachineContainers.objects.all()

    def update(self, request, pk, *args, **kwargs):
        data = super().update(request, pk, *args, **kwargs)
        machine = request.user.machine
        if machine.machine_status == Machine.MachineStates.OFF:
            containers = MachineContainers.objects.filter(
                machine__customuser=self.request.user
            )
            ingredients = containers.filter(container_number__gte=3)
            teas = containers.filter(container_number__lte=2)
            ingredients = IngredientsConatainerSerializer(ingredients, many=True)
            teas = TeasConatainerSerializer(teas, many=True)
            update_all_containers.delay(
                {
                    "tea_containers": teas.data,
                    "ingredient_containers": ingredients.data,
                },
                machine.machine_id,
            )
        else:
            container = MachineContainers.objects.get(pk=pk)
            if container.tea is not None:
                data = TeaSerializer(container.tea)
            elif container.ingredient is not None:
                data = IngredientSerializer(container.ingredient)
            update_single_container.delay(
                data.data, container.container_number, machine.machine_id
            )
        return Response(data.data)

    def get_queryset(self):
        return MachineContainers.objects.filter(
            Q(machine__customuser=self.request.user) & (Q(container_number__lte=2))
        )


class UpdateIngredientContainersView(generics.UpdateAPIView):
    """
    List or edit ingredient containers
    """

    serializer_class = UpdateIngredientsConatainerSerializer
    permission_classes = [IsOwnerOrAdmin]
    queryset = MachineContainers.objects.all()

    def get_queryset(self):
        return MachineContainers.objects.filter(
            Q(machine__customuser=self.request.user) & (Q(container_number__gte=3))
        )

    def update(self, request, pk, *args, **kwargs):
        data = super().update(request, pk, *args, **kwargs)
        machine = request.user.machine
        if machine.machine_status == Machine.MachineStates.OFF:
            containers = MachineContainers.objects.filter(
                machine__customuser=self.request.user
            )
            ingredients = containers.filter(container_number__gte=3)
            teas = containers.filter(container_number__lte=2)
            ingredients = IngredientsConatainerSerializer(ingredients, many=True)
            teas = TeasConatainerSerializer(teas, many=True)
            update_all_containers.delay(
                {
                    "tea_containers": teas.data,
                    "ingredient_containers": ingredients.data,
                },
                machine.machine_id,
            )
        else:
            container = MachineContainers.objects.get(pk=pk)
            update_single_container.delay(
                data.data, machine.id, container.container_number
            )
        return data


class GetMachineContainers(generics.ListAPIView):

    queryset = MachineContainers.objects.all()
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = IngredientsConatainerSerializer

    def get_queryset(self):
        return MachineContainers.objects.filter(machine__customuser=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        ingredients = queryset.filter(container_number__gte=3)
        teas = queryset.filter(container_number__lte=2)
        ingredients = IngredientsConatainerSerializer(ingredients, many=True)
        teas = TeasConatainerSerializer(teas, many=True)
        return Response(
            {"tea_containers": teas.data, "ingredient_containers": ingredients.data}
        )


class ListPublicRecipes(generics.ListAPIView):
    """
    List public recipes with filters
    """

    class RecipesSetPagination(pagination.PageNumberPagination):
        page_size = 6
        page_size_query_param = "size"
        max_page_size = 6

    # serializer_class = RecipesSerializer2
    serializer_class = RecipesSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Recipes.objects.filter(is_public=True)
    pagination_class = RecipesSetPagination

    def get_queryset(self):
        try:
            return filter_recipes(
                self.request.query_params, Recipes.objects.filter(is_public=True)
            )
        except ValueError:
            raise WrongQuerystringValue()


class UserRecipesViewSet(viewsets.ModelViewSet):
    """
    Used to do all staff with logged user recipes. Doesnt have access to other recipes.
    Use PATCH to update existing ingredients in recipes
    Use PUT to create new recipe or pass id to edit existing
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
    # serializer_class = RecipesSerializer2
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

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH", "POST"]:
            return WriteRecipesSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredients.objects.all()
    permission_classes_by_action = {
        "list": [permissions.IsAuthenticated],
    }

    def get_permissions(self):
        if self.action in self.permission_classes_by_action:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        else:
            return [permissions.IsAdminUser()]


class DeleteRecipeIngredient(generics.DestroyAPIView):
    queryset = IngredientsRecipes.objects.all()
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = IngredientsRecipesSerializer


class ListTeas(generics.ListAPIView):
    queryset = Teas.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeaSerializer


class ListIngredients(generics.ListAPIView):
    queryset = Ingredients.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IngredientSerializer


class SendRecipeView(APIView):
    queryset = IngredientsRecipes.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PrepareRecipeSerializer

    def post(self, request, format=None):
        self.check_permissions(request)
        try:
            id = request.data["id"]
        except KeyError:
            raise ValidationError({"id": "Field is required."})
        try:
            recipe = Recipes.objects.get(pk=id)
        except ObjectDoesNotExist:
            raise ValidationError({"detail": "Recipe does not exist."})
        machine = Machine.objects.get(pk=request.user.machine.machine_id)
        if machine.machine_status == 0:
            raise ValidationError({"detail": "Machine is not connected."})
        if not machine.is_mug_ready:
            raise ValidationError({"detail": "Mug is not ready."})
        tea_containers = MachineContainers.objects.filter(
            Q(machine=machine) & Q(container_number__lte=2)
        )
        no_tea = True
        for tea_container in tea_containers:
            if tea_container.tea == recipe.tea_type:
                if tea_container.ammount >= recipe.tea_herbs_ammount:
                    no_tea = False
                else:
                    raise ValidationError(
                        {"detail": "Not enough tea herbs in container."}
                    )
                break
        if no_tea:
            raise ValidationError(
                {"detail": "Given tea type is not available in your tea containers."}
            )

        ingredient_containers = MachineContainers.objects.filter(
            Q(machine=request.user.machine) & Q(container_number__gte=3)
        )

        ingredients = IngredientsRecipes.objects.filter(recipe=recipe)
        no_ingredient = True
        for ingredient in ingredients:
            for ingredient_container in ingredient_containers:
                if ingredient_container.ingredient == ingredient.ingredient:
                    if ingredient_container.ammount >= ingredient.ammount:
                        no_ingredient = False
                    else:
                        raise ValidationError(
                            {"detail": "Not enough ingredient in container."}
                        )
                    break
            if no_ingredient:
                raise ValidationError(
                    {
                        "detail": "Some of given ingredients is not avaliable in yuor ingredient containers."
                    }
                )
        if not machine.water_container_weight >= (recipe.tea_portion + 60):
            raise ValidationError({"detail": "Not enough water."})

        serializer = PrepareRecipeSerializer(recipe)
        send_recipe.delay(serializer.data, machine.id)
        return Response({}, status=200)


class AddToFavouritesView(generics.UpdateAPIView):

    serializer_class = FavouritesSerializer
    queryset = Recipes.objects.all()
    permission_classes = [IsAuthorOrAdmin]

    def get_queryset(self):
        return Recipes.objects.filter(author=self.request.user)

    def update(self, request, pk, *args, **kwargs):
        recipe = Recipes.objects.get(pk=pk)
        was_favourite = recipe.is_favourite
        data = super().update(request, *args, **kwargs)
        machine = request.user.machine
        if machine.machine_status == Machine.MachineStates.OFF:
            # Machine is off
            recipes = Recipes.objects.filter(
                Q(author=request.user) & Q(is_favourite=True)
            )
            recipes = PrepareRecipeSerializer(recipes, many=True)
            favourites_edit_offline.delay(recipes.data, machine.machine_id)
        else:
            
            recipe = PrepareRecipeSerializer(recipe)
            if data.data["is_favourite"]:
                # Add to favourites
                if not was_favourite:
                    favourites_edit_online.delay(recipe.data, "add", machine.machine_id)
            else:
                if was_favourite:
                    # Delete from favourites
                    favourites_edit_online.delay(
                        {"id": recipe.data["id"]}, "delete", machine.machine_id
                    )
        return data
