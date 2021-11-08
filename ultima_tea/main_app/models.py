from django.db import models

# Create your models here.
from django.db import models
from authorization.models import CustomUser, Machine
from django.db.models.deletion import CASCADE, SET_DEFAULT

# Create your models here.
class State(models.IntegerChoices):
    LIQUID = 1
    SOLID = 2


class UnitTypes(models.IntegerChoices):
    METRICAL = 1
    IMPERIAL = 2


class Ingerdients(models.Model):
    ingredient_name = models.CharField()
    type = models.IntegerField(choices=State.choices)

    class Meta:
        db_table = "ingredients"


class Teas(models.Model):
    tea_name = models.CharField(max_length=255, primary_key=True)

    class Meta:
        db_table = "teas"


class Recipes(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    orginal_author = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    last_modification = models.DateTimeField(auto_now_add=True)
    descripction = models.TextField(max_length=1023, default="")
    recipe_name = models.CharField()
    overall_upvotes = models.IntegerField(default=0)
    last_month_upvotes = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)
    brewing_temperature = models.FloatField(default=80)
    brewing_time = models.FloatField(default=60)
    mixing_time = models.FloatField(default=15)
    is_favourite = models.BooleanField(default=False)
    tea_type = models.ForeignKey(Teas, on_delete=models.CASCADE)
    tea_herbs_ammount = models.FloatField()
    tea_portion = models.FloatField(default=200)

    class Meta:
        db_table = "recipes"
        ordering = (
            "-is_favourite",
            "recipe_name",
        )

    def __str__(self):
        return self.recipe_name + ": " + self.descripction


# In db all ammounts will be stored in one type of unit, and will be converted on demand. Default in SI
class IngredientsRecipes(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingerdients, on_delete=models.CASCADE)
    # Unit in which recipe was created
    ammount = models.FloatField()

    class Meta:
        db_table = "ingredients_recipes"


class Unit(models.Model):
    unit = models.IntegerField(choices=State.choices)
    unit_type = models.IntegerField(choices=UnitTypes.choices)
    # TODO Delete default
    ratio_to_metrical = models.FloatField(default=0.035274)


class UserSettings(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000, default="Brak opisu")
    units = models.ForeignKey(
        Unit, on_delete=models.CASCADE, default=UnitTypes.METRICAL
    )

    class Meta:
        db_table = "user_settings"


class MachineContainers(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingerdients, on_delete=models.CASCADE)
    ammount = models.FloatField(default=0)

    class Meta:
        db_table = "machine_container"


class FavoriteRecipes(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=CASCADE)

    class Meta:
        db_table = "favorite_recipes"


class History(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "history"
