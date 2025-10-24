"""Placeholder initial migration for the `clone` app.

This file is intentionally minimal: it creates no operations but provides
the expected migration node so subsequent placeholder migrations can
depend on it. If you have a real 0001_initial migration in source control
that was accidentally removed, restore that instead of using this file.
"""
from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = []
# Generated minimal initial migration for the `clone` app.
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=75, verbose_name='Tag')),
                ('slug', models.SlugField(default=uuid.uuid1, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('picture', models.ImageField(upload_to='')),
                ('caption', models.CharField(max_length=10000, verbose_name='Caption')),
                ('posted', models.DateField(auto_now_add=True)),
                ('likes', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clone.post')),
            ],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower', models.ForeignKey(related_name='follower', on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('following', models.ForeignKey(related_name='following', on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('following', models.ForeignKey(related_name='stream_following', null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('post', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='clone.post')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(related_name='tags', to='clone.Tag'),
        ),
    ]
