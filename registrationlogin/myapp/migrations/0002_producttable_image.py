# Generated by Django 5.0 on 2024-01-29 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producttable',
            name='image',
            field=models.ImageField(default=0, upload_to='image'),
            preserve_default=False,
        ),
    ]
