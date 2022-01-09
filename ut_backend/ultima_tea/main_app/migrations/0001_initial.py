# Generated by Django 4.0 on 2022-01-09 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authorization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredient_name', models.CharField(max_length=32)),
                ('type', models.IntegerField(choices=[(1, 'Liquid'), (2, 'Solid')])),
                ('opening_percentage', models.IntegerField(default=0)),
                ('pass_time', models.IntegerField(default=0)),
                ('weight_offset', models.IntegerField(default=0)),
                ('density', models.FloatField(default=0)),
            ],
            options={
                'db_table': 'ingredients',
            },
        ),
        migrations.CreateModel(
            name='Recipes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_modification', models.DateTimeField(auto_now_add=True)),
                ('descripction', models.TextField(default='Brak', max_length=256)),
                ('recipe_name', models.CharField(max_length=64)),
                ('score', models.FloatField(default=0)),
                ('votes', models.IntegerField(default=0)),
                ('is_public', models.BooleanField(default=False)),
                ('brewing_temperature', models.FloatField(default=80)),
                ('brewing_time', models.FloatField(default=60)),
                ('mixing_time', models.FloatField(default=15)),
                ('is_favourite', models.BooleanField(default=False)),
                ('tea_herbs_ammount', models.FloatField(default=15)),
                ('tea_portion', models.FloatField(default=200)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authorization.customuser')),
            ],
            options={
                'db_table': 'recipes',
                'ordering': ('-is_favourite', 'recipe_name'),
            },
        ),
        migrations.CreateModel(
            name='Teas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tea_name', models.CharField(max_length=32)),
                ('density', models.FloatField(default=0)),
                ('opening_percentage', models.IntegerField(default=0)),
                ('pass_time', models.IntegerField(default=0)),
                ('weight_offset', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'teas',
            },
        ),
        migrations.CreateModel(
            name='VotedRecipes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.recipes')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authorization.customuser')),
            ],
            options={
                'db_table': 'voted_recipes',
            },
        ),
        migrations.AddField(
            model_name='recipes',
            name='tea_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.teas'),
        ),
        migrations.CreateModel(
            name='MachineContainers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ammount', models.FloatField(default=0, null=True)),
                ('container_number', models.IntegerField(choices=[(1, 'first_container_weight'), (2, 'second_container_weight'), (3, 'third_container_weight'), (4, 'fourth_container_weight')], default=0)),
                ('ingredient', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.ingredients')),
                ('machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='machine_containers', to='authorization.machine')),
                ('tea', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.teas')),
            ],
            options={
                'db_table': 'machine_container',
            },
        ),
        migrations.CreateModel(
            name='IngredientsRecipes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ammount', models.FloatField()),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.ingredients')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='main_app.recipes')),
            ],
            options={
                'db_table': 'ingredients_recipes',
            },
        ),
        migrations.AddIndex(
            model_name='votedrecipes',
            index=models.Index(fields=['user', 'recipe'], name='voted_recip_user_id_de5356_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='votedrecipes',
            unique_together={('user', 'recipe')},
        ),
        migrations.AddIndex(
            model_name='recipes',
            index=models.Index(fields=['author'], name='recipes_author__745c9c_idx'),
        ),
        migrations.AddIndex(
            model_name='machinecontainers',
            index=models.Index(fields=['machine'], name='machine_con_machine_f0874a_idx'),
        ),
        migrations.AddIndex(
            model_name='ingredientsrecipes',
            index=models.Index(fields=['recipe'], name='ingredients_recipe__5c2af9_idx'),
        ),
    ]
