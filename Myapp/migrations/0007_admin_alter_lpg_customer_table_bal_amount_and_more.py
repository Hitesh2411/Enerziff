# Generated by Django 4.2.4 on 2023-09-30 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0006_transaction_details_phonenumber'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('password', models.TextField(max_length=20)),
                ('email', models.CharField(max_length=30)),
            ],
        ),
        migrations.AlterField(
            model_name='lpg_customer_table',
            name='BAL_AMOUNT',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='lpg_customer_table',
            name='BAL_LPG',
            field=models.FloatField(),
        ),
    ]
