# Generated by Django 5.1.6 on 2025-03-12 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_platform', '0005_alter_customer_campaign_alter_customer_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='communication_method',
            field=models.CharField(choices=[('SMS', 'SMS'), ('Email', 'Email'), ('WhatsApp', 'WhatsApp')], default='SMS', max_length=10),
        ),
    ]
