from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from authorization.models import Machine
from main_app.models import *
from django.db.models import Q


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
    ingredient = IngredientSerializer(required=True, allow_null=True)

    class Meta:
        model = MachineContainers
        fields = (
            "id",
            "ammount",
            "ingredient",
            "container_number",
        )


class TeasConatainerSerializer(serializers.ModelSerializer):
    tea = TeaSerializer(required=True, allow_null=True)

    class Meta:
        model = MachineContainers
        fields = (
            "id",
            "ammount",
            "tea",
            "container_number",
        )


class UpdateIngredientsConatainerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True, allow_null=True)

    def update(self, instance, validated_data):
        try:
            id = validated_data.pop("id")
        except KeyError:
            raise serializers.ValidationError({"id": "Field is required."})
        try:
            if id is None:
                instance.ingredient = id
            else:
                ingredient = Ingredients.objects.get(pk=id)
                instance.ingredient = ingredient
            instance.save()
            return instance
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Ingredient does not exist.")

    class Meta:
        model = MachineContainers
        fields = ("id",)


class UpdateTeasConatainerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True, allow_null=True)

    def update(self, instance, validated_data):
        try:
            id = validated_data.pop("id")
        except KeyError:
            raise serializers.ValidationError({"id": "Field is required."})
        try:
            if id is None:
                instance.tea = id
            else:
                tea = Teas.objects.get(pk=id)
                instance.tea = tea

            instance.save()
            return instance
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Tea does not exist.")

    class Meta:
        model = MachineContainers
        fields = ("id",)


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
        if instance.is_public:
            if not (
                len(validated_data.keys()) == 1 and "descripction" in validated_data
            ):
                # Cant update public recipe
                try:
                    if validated_data["is_public"]:
                        raise serializers.ValidationError(
                            {"is_public": "You cant modify public recipe."}
                        )
                    # Change to private - clear upvotes
                    instance.overall_upvotes = 0
                    instance.last_month_upvotes = 0
                    instance.save()
                except KeyError:
                    raise serializers.ValidationError(
                        {"is_public": "You cant modify public recipe."}
                    )

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
        exclude = ("author", "votes", "score", "last_modification")


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
    voted = serializers.SerializerMethodField()
    voted_score = serializers.SerializerMethodField()

    def get_voted(self, obj):
        try:
            VotedRecipes.objects.get(Q(recipe=obj.id) & Q(user=self.context["user"]))
            return True
        except VotedRecipes.DoesNotExist:
            return False
        except KeyError:
            return False

    def get_voted_score(self, obj):
        try:
            return VotedRecipes.objects.get(
                Q(recipe=obj.id) & Q(user=self.context["user"])
            ).score
        except VotedRecipes.DoesNotExist:
            return 0
        except KeyError:
            return 0

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


class RecipeVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = VotedRecipes
        fields = "__all__"
        extra_kwargs = {"score": {"required": True}}

    def validate_score(self, value):
        if value is None:
            raise ValidationError({"score": "This field is required."})
        if value > 5 or value < 0:
            raise ValidationError({"score": "Wrong score values. Range is <0;5>."})
        return value
