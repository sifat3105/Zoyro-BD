# Generated by Django 5.2 on 2025-04-24 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeliverySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maxbuy', models.PositiveIntegerField(default=2000)),
            ],
        ),
    ]
