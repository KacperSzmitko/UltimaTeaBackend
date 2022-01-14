from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = "main_app"

recipes_router = DefaultRouter()
recipes_router.register("recipes", UserRecipesViewSet)
ingredients_router = DefaultRouter()
ingredients_router.register("ingredients", IngredientsViewSet)
teas_router = DefaultRouter()
teas_router.register("teas", TeasViewSet)
machine_router = DefaultRouter()
machine_router.register("machine", MachineInfoViewSet)


urlpatterns = [
    # path("machine/<slug:pk>", GetMachineInfo.as_view(), name="get_machine"),
    path("public_recipes/", ListPublicRecipes.as_view(), name="list_public_recipes"),
    path("check_token/", CheckTokenView.as_view(), name='check_token'),
    path("send_recipe/", SendRecipeView.as_view(), name="send_recipe"),
        path(
        "machine/containers/",
        GetMachineContainers.as_view(),
        name="list_machine_containers",
    ),
    path(
        "machine/containers/tea/<int:pk>/",
        UpdateTeaContainersView.as_view(),
        name="update_tea_container",
    ),
    path(
        "machine/containers/ingredient/<int:pk>/",
        UpdateIngredientContainersView.as_view(),
        name="update_ingredient_container",
    ),
    path("", include(recipes_router.urls), name="user_recipes"),
    path("", include(ingredients_router.urls), name="ingredients"),
    path("", include(teas_router.urls), name="teas"),
    path("", include(machine_router.urls), name="machine"),
    path(
        "recipe_ingredient/<int:pk>/",
        DeleteRecipeIngredient.as_view(),
        name="delete_recipe_ingredient",
    ),
    path("teas/", ListTeas.as_view(), name="list_teas"),
    path("send_recipe/", SendRecipeView.as_view(), name="send_recipe"),
    path(
        "favourites_edit/<int:pk>/",
        AddToFavouritesView.as_view(),
        name="add_to_favourites",
    ),
]
