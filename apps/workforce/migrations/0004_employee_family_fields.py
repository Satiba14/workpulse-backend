from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # Replace '0003_employeedocument...' with your actual last migration name
        ('workforce', '0003_employeedocumentmaster_document_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10),
        ),
        migrations.AddField(
            model_name='employee',
            name='blood_group',
            field=models.CharField(blank=True, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], max_length=5),
        ),
        migrations.AddField(
            model_name='employee',
            name='marital_status',
            field=models.CharField(blank=True, choices=[('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced'), ('widowed', 'Widowed')], max_length=15),
        ),
        migrations.AddField(
            model_name='employee',
            name='father_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='employee',
            name='mother_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='employee',
            name='spouse_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='employee',
            name='emergency_contact_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='employee',
            name='emergency_contact_phone',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='employee',
            name='emergency_contact_relation',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]