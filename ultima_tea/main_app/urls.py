from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
app_name = 'main_app'

router = DefaultRouter()
router.register('recipes',UserRecipes)

urlpatterns = [
    path('machine/',ListMachines.as_view(), name='list_machines'),
    path('machine/<slug:pk>',GetMachineInfo.as_view(), name='get_machine'),
    path('machine/<slug:pk>/containers/',GetMachineContainers.as_view(), name='get_machine_containers'),
    path('public_recipes/',ListPublicRecipes.as_view(), name='list_public_recipes'),
    path('',include(router.urls))
]