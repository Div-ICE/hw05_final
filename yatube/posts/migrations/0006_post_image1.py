# Generated by Django 2.2.16 on 2022-02-08 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20220209_0336'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image1',
            field=models.ImageField(blank=True, help_text='Загрузите изображение1', upload_to='posts/', verbose_name='Картинка1'),
        ),
    ]
