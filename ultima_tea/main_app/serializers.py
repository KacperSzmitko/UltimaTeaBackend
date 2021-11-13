from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import request
from rest_framework import fields, serializers, validators
from authorization.models import Machine
from main_app.models import *


class MachineInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = "__all__"


class MachineContainersSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineContainers
        fields = ("ammount", "ingredient", "container_number")


class IngredientSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = Ingerdients
        fields = (
            "ingredient_name",
            "type",
        )

    def get_type(self, obj):
        "Convert enum to readable value"
        return obj.get_type_display()


class IngredientsRecipesSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()
    # Id is required when yuo try to send PATCH
    id = serializers.IntegerField(required=False, write_only=False)

    class Meta:
        model = IngredientsRecipes
        fields = ("ammount", "ingredient", "id")

    def validate(self, attrs):
        """
        Validate if ingredient object exist
        """
        if self.context["request"].method == "PATCH":
            """
            For PATCH ingredient argument is optional
            """
            if "ingredient" in attrs:
                try:
                    Ingerdients.objects.get(**attrs["ingredient"])
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("Ingredient does not exist")
        else:
            try:
                Ingerdients.objects.get(**attrs["ingredient"])
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Ingredient does not exist")
        return super().validate(attrs)

    def validate_id(self, value):
        """
        If id is specified validate if object exist
        """
        if IngredientsRecipes.objects.filter(pk=value).exists():
            return value
        raise serializers.ValidationError("Object does not exist")


class RecipesSerializer(serializers.ModelSerializer):
    ingredients = IngredientsRecipesSerializer(many=True)
    # author = serializers.SerializerMethodField()

    def create(self, validated_data):
        # Get parts with ingredients and ammounts
        ingredients_recipes_data = validated_data.pop("ingredients")
        recipe = Recipes.objects.create(**validated_data)
        # For every ingredient iwth ammount create new IngredientRecipe object
        for ingredients_data in ingredients_recipes_data:
            # Get specified Ingredient object
            ingredient = Ingerdients.objects.get(**ingredients_data["ingredient"])
            IngredientsRecipes.objects.create(
                recipe=recipe,
                ammount=ingredients_data["ammount"],
                ingredient=ingredient,
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_recipes_data = validated_data.pop("ingredients")
        recipe = super().update(instance, validated_data)
        for ingredients_data in ingredients_recipes_data:
            # If method is PATCH make validation which fields was specified
            if self.context["request"].method == "PATCH":
                if "id" in ingredients_data:
                    instance = IngredientsRecipes.objects.filter(
                        pk=ingredients_data["id"]
                    )
                    if "ingredient" in ingredients_data:
                        ingredient = Ingerdients.objects.get(
                            **ingredients_data["ingredient"]
                        )
                    else:
                        ingredient = False
                else:
                    raise serializers.ValidationError(
                        {"ingredients": [{"id": "Field is required."}]}
                    )

                if "ammount" in ingredients_data:
                    ammount = ingredients_data["ammount"]
                    if ingredient != False:
                        instance.update(ingredient=ingredient, ammount=ammount)
                    else:
                        instance.update(ammount=ammount)
                else:
                    if ingredient != False:
                        instance.update(ingredient=ingredient)
                        return recipe
            else:
                # For PUT just update existing records
                ingredient = Ingerdients.objects.get(**ingredients_data["ingredient"])
                ingredient_recpie = IngredientsRecipes.objects.filter(
                    pk=ingredients_data["id"]
                )
                ingredient_recpie.update(
                    recipe=recipe,
                    ammount=ingredients_data["ammount"],
                    ingredient=ingredient,
                )
        return recipe

    class Meta:
        model = Recipes
        exclude = ("author",)
