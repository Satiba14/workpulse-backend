from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        # Replace with your last actual migration name
        ('workforce', '0004_employee_family_fields'),
    ]

    operations = [
        migrations.AddField(model_name='employee', name='current_address',
            field=models.TextField(blank=True)),
        migrations.AddField(model_name='employee', name='current_pincode',
            field=models.CharField(blank=True, max_length=10)),
        migrations.AddField(model_name='employee', name='current_city',
            field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='employee', name='current_state',
            field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='employee', name='permanent_address',
            field=models.TextField(blank=True)),
        migrations.AddField(model_name='employee', name='permanent_pincode',
            field=models.CharField(blank=True, max_length=10)),
        migrations.AddField(model_name='employee', name='permanent_city',
            field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='employee', name='permanent_state',
            field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='employee', name='aadhaar_address',
            field=models.TextField(blank=True)),
    ]