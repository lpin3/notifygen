from django.db import migrations, models
import django.db.models.deletion


def backfill_device_access_status(apps, schema_editor):
    DispositivoMobile = apps.get_model('crr', 'DispositivoMobile')

    for dispositivo in DispositivoMobile.objects.all():
        if not dispositivo.ativo:
            dispositivo.status_acesso = 'blocked'
        elif dispositivo.ativado:
            dispositivo.status_acesso = 'approved'
        else:
            dispositivo.status_acesso = 'pending'
        dispositivo.save(update_fields=['status_acesso'])


class Migration(migrations.Migration):

    dependencies = [
        ('crr', '0018_rename_imei_to_device_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispositivomobile',
            name='aprovado_em',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Aprovado em'),
        ),
        migrations.AddField(
            model_name='dispositivomobile',
            name='motivo_bloqueio',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Motivo do bloqueio'),
        ),
        migrations.AddField(
            model_name='dispositivomobile',
            name='solicitado_em',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Solicitado em'),
        ),
        migrations.AddField(
            model_name='dispositivomobile',
            name='solicitado_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='dispositivos_solicitados',
                to='crr.agente',
                verbose_name='Solicitado por',
            ),
        ),
        migrations.AddField(
            model_name='dispositivomobile',
            name='status_acesso',
            field=models.CharField(
                choices=[('pending', 'Pendente'), ('approved', 'Aprovado'), ('blocked', 'Bloqueado')],
                default='pending',
                help_text='Controla se o dispositivo esta pendente, aprovado ou bloqueado para uso no app.',
                max_length=20,
                verbose_name='Status de Acesso',
            ),
        ),
        migrations.RunPython(backfill_device_access_status, migrations.RunPython.noop),
    ]
