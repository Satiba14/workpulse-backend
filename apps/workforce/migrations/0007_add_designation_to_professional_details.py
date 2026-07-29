from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0006_alter_employeedocumentmaster_file_path_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeprofessionaldetails',
            name='designation',
            field=models.CharField(
                max_length=100,
                blank=True,
                help_text='Job title / role e.g. Senior Developer, QA Engineer',
            ),
        ),
    ]