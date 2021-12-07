from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from authorization.models import Machine
from main_app.models import *


class IngredientSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Ingredients
        fields = (
            "ingredient_name",
            "type",
            "id",
        )

    def get_type(self, obj):
        "Convert enum to readable value"
        return obj.get_type_display()


class TeaSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Teas
        fields = (
            "tea_name",
            "id",
        )


class IngredientsConatainerSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = MachineContainers
        fields = (
            "id",
            "ammount",
            "ingredient",
            "container_number",
        )


class TeasConatainerSerializer(serializers.ModelSerializer):
    tea = TeaSerializer(required=True)

    class Meta:
        model = MachineContainers
        fields = (
            "id",
            "ammount",
            "tea",
            "container_number",
        )


class UpdateIngredientsConatainerSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.IntegerField(required=True)

    def update(self, instance, validated_data):
        try:
            ingredient_id = validated_data.pop("ingredient_id")
        except KeyError:
            raise serializers.ValidationError({"ingredient_id": "Field is required."})
        try:
            ingredient = Ingredients.objects.get(pk=ingredient_id)
            instance.ingredient = ingredient
            instance.save()
            return instance
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Ingredient does not exist.")

    class Meta:
        model = MachineContainers
        fields = ("ingredient_id",)


class UpdateTeasConatainerSerializer(serializers.ModelSerializer):
    tea_id = serializers.IntegerField(required=True)

    def update(self, instance, validated_data):
        try:
            tea_id = validated_data.pop("tea_id")
        except KeyError:
            raise serializers.ValidationError({"tea_id": "Field is required."})
        try:
            tea = Teas.objects.get(pk=tea_id)
            instance.tea = tea
            instance.save()
            return instance
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Tea does not exist.")

    class Meta:
        model = MachineContainers
        fields = ("tea_id",)


class MachineInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = "__all__"


class WriteIngredientsRecipesSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.IntegerField(required=True)
    # Id is required when yuo try to send PATCH
    id = serializers.IntegerField(required=False, write_only=False)

    class Meta:
        model = IngredientsRecipes
        fields = (
            "ammount",
            "id",
            "ingredient_id",
        )

    def validate(self, attrs):
        # Validate if ingredient object exist
        if self.context["request"].method == "PATCH":
            # For PATCH ingredient argument is optional
            if "ingredient_id" in attrs:
                try:
                    Ingredients.objects.get(pk=attrs["ingredient_id"])
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("Ingredient does not exist")
                except Ingredients.MultipleObjectsReturned:
                    raise serializers.ValidationError("Ingredient was not specified")
        else:
            try:
                Ingredients.objects.get(pk=attrs["ingredient_id"])
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Ingredient does not exist")
        return super().validate(attrs)

    def validate_id(self, value):
        # If id is specified validate if object exist
        if IngredientsRecipes.objects.filter(pk=value).exists():
            return value
        raise serializers.ValidationError("Object does not exist")


class WriteRecipesSerializer(serializers.ModelSerializer):
    ingredients = WriteIngredientsRecipesSerializer(many=True)
    # author = serializers.SerializerMethodField()

    def create(self, validated_data):
        # Get parts with ingredients and ammounts
        ingredients_recipes_data = validated_data.pop("ingredients")
        recipe = Recipes.objects.create(**validated_data)
        # For every ingredient iwth ammount create new IngredientRecipe object
        for ingredients_data in ingredients_recipes_data:
            # Get specified Ingredient object
            ingredient = Ingredients.objects.get(pk=ingredients_data["ingredient_id"])
            IngredientsRecipes.objects.create(
                recipe=recipe,
                ammount=ingredients_data["ammount"],
                ingredient=ingredient,
            )
        return recipe

    def update(self, instance, validated_data):
        if self.partial:
            # PATCH method
            try:
                ingredients_recipes_data = validated_data.pop("ingredients")
                recipe = super().update(instance, validated_data)
                if ingredients_recipes_data == []:
                    # Empty inredients
                    return recipe
            except KeyError:
                # No ingredients
                recipe = super().update(instance, validated_data)
                return recipe
            for ingredients_data in ingredients_recipes_data:
                if "id" not in ingredients_data:
                    # No id of recipe to edit - raise error
                    raise serializers.ValidationError({"id": "Field is required."})
                instance = IngredientsRecipes.objects.filter(pk=ingredients_data["id"])
                if "ingredient_id" in ingredients_data:
                    ingredient = Ingredients.objects.get(
                        pk=ingredients_data["ingredient_id"]
                    )
                else:
                    ingredient = None

                if "ammount" in ingredients_data:
                    ammount = ingredients_data["ammount"]
                    if ingredient is not None:
                        instance.update(ingredient=ingredient, ammount=ammount)
                    else:
                        instance.update(ammount=ammount)
                else:
                    if ingredient is not None:
                        instance.update(ingredient=ingredient)
                        return recipe
        else:
            # PUT method
            try:
                ingredients_recipes_data = validated_data.pop("ingredients")
                recipe = super().update(instance, validated_data)
                IngredientsRecipes.objects.filter(recipe=recipe).delete()
                if ingredients_recipes_data == []:
                    # Empty ingredients - delete all existing
                    return recipe
            except KeyError:
                # No ingredients is prohibited
                raise serializers.ValidationError({"ingredients": "Field is required"})
            for ingredients_data in ingredients_recipes_data:
                ingredient = Ingredients.objects.get(
                    pk=ingredients_data["ingredient_id"]
                )
                # Id not specified - create new one
                IngredientsRecipes.objects.create(
                    recipe=recipe,
                    ammount=ingredients_data["ammount"],
                    ingredient=ingredient,
                )
        return recipe

    class Meta:
        model = Recipes
        exclude = ("author",)


class IngredientsRecipesSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = IngredientsRecipes
        fields = (
            "ammount",
            "ingredient",
            "id",
        )


class RecipesSerializer(serializers.ModelSerializer):
    ingredients = IngredientsRecipesSerializer(many=True)
    tea_type = TeaSerializer()

    class Meta:
        model = Recipes
        fields = "__all__"


class PrepareRecipeIngredientRecipesSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = IngredientsRecipes
        fields = (
            "ingredient",
            "ammount",
        )


class PrepareRecipeSerializer(serializers.ModelSerializer):
    tea_type = TeaSerializer(read_only=True)
    ingredients = PrepareRecipeIngredientRecipesSerializer(many=True)
    currnet_tea_portion = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Recipes
        fields = (
            "recipe_name",
            "brewing_temperature",
            "brewing_time",
            "mixing_time",
            "tea_type",
            "ingredients",
            "tea_herbs_ammount",
            "tea_portion",
            "id",
            "currnet_tea_portion",
        )

    def get_currnet_tea_portion(self, obj):
        currnet_tea_portion = self.context.get("tea_portion", obj.tea_portion)
        if currnet_tea_portion != "":
            return currnet_tea_portion 
        return None


class FavouritesSerializer(serializers.ModelSerializer):
    is_favourite = serializers.BooleanField(required=True)

    class Meta:
        model = Recipes
        fields = ("is_favourite",)
