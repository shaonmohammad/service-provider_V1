# Generated by Django 5.1.6 on 2025-03-11 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_platform', '0003_customer_is_given_review_customer_is_sent_email_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='customer',
        ),
        migrations.AddField(
            model_name='customer',
            name='campaign',
            field=models.ManyToManyField(to='service_platform.campaign'),
        ),
    ]
