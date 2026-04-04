from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crr', '0017_lowercase_situacao_entrega_choices'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dispositivomobile',
            old_name='imei',
            new_name='device_id',
        ),
        migrations.AlterField(
            model_name='dispositivomobile',
            name='device_id',
            field=models.CharField(
                blank=True,
                help_text='Identificador unico gerado pelo app mobile (ex.: UUID)',
                max_length=64,
                null=True,
                unique=True,
                verbose_name='Identificador do Dispositivo',
            ),
        ),
    ]
