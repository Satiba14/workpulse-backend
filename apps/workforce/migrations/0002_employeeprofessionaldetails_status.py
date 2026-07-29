
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeprofessionaldetails',
            name='status',
            field=models.CharField(choices=[('billable', 'Billable'), ('non_billable', 'Non-Billable'), ('buffer', 'Buffer'), ('inactive', 'Inactive')], default='billable', max_length=20),
        ),
    ]
