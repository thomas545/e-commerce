# Generated by Django 2.1.7 on 2019-04-12 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0003_auto_20190412_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketingpreference',
            name='mailchimp_msg',
            field=models.TextField(blank=True, null=True),
        ),
    ]