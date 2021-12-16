from django.db import models

# Create your models here.
from django.db import models
from django.db.models import fields
from authorization.models import CustomUser, Machine
from django.db.models.deletion import CASCADE, SET_DEFAULT

# Create your models here.
class State(models.IntegerChoices):
    LIQUID = 1
    SOLID = 2


class UnitTypes(models.IntegerChoices):
    METRICAL = 1
    IMPERIAL = 2


class Ingredients(models.Model):
    ingredient_name = models.CharField(max_length=32)
    type = models.IntegerField(choices=State.choices)

    class Meta:
        db_table = "ingredients"

    def __str__(self):
        return self.ingredient_name


class Teas(models.Model):
    tea_name = models.CharField(max_length=32)

    class Meta:
        db_table = "teas"

    def __str__(self):
        return self.tea_name


class Recipes(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    orginal_author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="original_author",
    )
    last_modification = models.DateTimeField(auto_now_add=True)
    descripction = models.TextField(max_length=512, default="Brak")
    recipe_name = models.CharField(max_length=128)
    score = models.FloatField(default=0)
    votes = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)
    brewing_temperature = models.FloatField(default=80)
    brewing_time = models.FloatField(default=60)
    mixing_time = models.FloatField(default=15)
    is_favourite = models.BooleanField(default=False)
    tea_type = models.ForeignKey(Teas, on_delete=models.CASCADE)
    tea_herbs_ammount = models.FloatField(default=15)
    tea_portion = models.FloatField(default=200)

    class Meta:
        db_table = "recipes"
        ordering = (
            "-is_favourite",
            "recipe_name",
        )
        indexes = [models.Index(fields=["author"])]

    def __str__(self):
        return self.recipe_name


# In db all ammounts will be stored in one type of unit, and will be converted on demand. Default in SI
class IngredientsRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name="ingredients"
    )
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    # Unit in which recipe was created
    ammount = models.FloatField()

    class Meta:
        db_table = "ingredients_recipes"
        indexes = [models.Index(fields=["recipe"])]

    def __str__(self):
        return self.recipe.recipe_name


class Units(models.Model):
    unit = models.IntegerField(choices=State.choices)
    unit_type = models.IntegerField(choices=UnitTypes.choices)
    # TODO Delete default
    ratio_to_metrical = models.FloatField(default=0.035274)


class UserSettings(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000, default="Brak opisu")
    units = models.ForeignKey(
        Units, on_delete=models.CASCADE, default=UnitTypes.METRICAL
    )

    class Meta:
        db_table = "user_settings"


class MachineContainers(models.Model):

    CONTAINER_NAME_CHOICES = (
        (1, "first_container_weight"),  # Tea
        (2, "second_container_weight"),  # Tea
        (3, "third_container_weight"),  # Ingredient
        (4, "fourth_container_weight"),  # Ingredient
    )

    machine = models.ForeignKey(
        Machine, on_delete=models.CASCADE, related_name="machine_containers"
    )
    ingredient = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, null=True, default=None
    )
    tea = models.ForeignKey(Teas, on_delete=models.CASCADE, null=True, default=None)
    ammount = models.FloatField(default=0, null=True)
    container_number = models.IntegerField(default=0, choices=CONTAINER_NAME_CHOICES)

    class Meta:
        db_table = "machine_container"
        indexes = [models.Index(fields=["machine"])]

    def __str__(self):
        return self.machine.machine_id


class VotedRecipes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    class Meta:
        db_table = "voted_recipes"
        unique_together = (("user", "recipe"))
        indexes = [models.Index(fields=["user", "recipe"])]
