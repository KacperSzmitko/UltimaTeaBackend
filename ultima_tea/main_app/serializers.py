from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
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
        model = Ingredients
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
                    Ingredients.objects.get(**attrs["ingredient"])
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("Ingredient does not exist")
        else:
            try:
                Ingredients.objects.get(**attrs["ingredient"])
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
            ingredient = Ingredients.objects.get(**ingredients_data["ingredient"])
            IngredientsRecipes.objects.create(
                recipe=recipe,
                ammount=ingredients_data["ammount"],
                ingredient=ingredient,
            )
        return recipe

    def update(self, instance, validated_data):
        if self.partial:
            """
            PATCH method
            """
            try:
                ingredients_recipes_data = validated_data.pop("ingredients")
                recipe = super().update(instance, validated_data)
                if ingredients_recipes_data == []:
                    """
                    Empty inredients
                    """
                    return recipe
            except KeyError:
                """
                No ingredients
                """
                recipe = super().update(instance, validated_data)
                return recipe
            for ingredients_data in ingredients_recipes_data:
                if "id" not in ingredients_data:
                    """
                    No id of recipe to edit - raise error
                    """
                    raise serializers.ValidationError({"id": "Field is required."})
                instance = IngredientsRecipes.objects.filter(pk=ingredients_data["id"])
                if "ingredient" in ingredients_data:
                    ingredient = Ingredients.objects.get(
                        **ingredients_data["ingredient"]
                    )
                else:
                    ingredient = None

                if "ammount" in ingredients_data:
                    ammount = ingredients_data["ammount"]
                    if ingredient != None:
                        instance.update(ingredient=ingredient, ammount=ammount)
                    else:
                        instance.update(ammount=ammount)
                else:
                    if ingredient != None:
                        instance.update(ingredient=ingredient)
                        return recipe
        else:
            """
            PUT method
            """
            try:
                ingredients_recipes_data = validated_data.pop("ingredients")
                recipe = super().update(instance, validated_data)
                IngredientsRecipes.objects.filter(recipe=recipe).delete()
                if ingredients_recipes_data == []:
                    """
                    Empty ingredients - delete all existing
                    """
                    return recipe
            except KeyError:
                """
                No ingredients is prohibited
                """
                raise serializers.ValidationError({"ingredients": "Field is required"})
            for ingredients_data in ingredients_recipes_data:
                ingredient = Ingredients.objects.get(**ingredients_data["ingredient"])
                """
                Id not specified - create new one
                """
                IngredientsRecipes.objects.create(
                    recipe=recipe,
                    ammount=ingredients_data["ammount"],
                    ingredient=ingredient,
                )
        return recipe

    class Meta:
        model = Recipes
        exclude = ("author",)
