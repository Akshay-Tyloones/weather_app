# Generated by Django 5.0.4 on 2024-04-30 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0006_alter_userdetails_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdetails',
            name='image_url',
            field=models.URLField(default=None, null=True),
        ),
    ]
