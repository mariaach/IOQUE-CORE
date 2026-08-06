from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='payment',
            name='payments_pa_stripe__6fe52c_idx',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='stripe_payment_intent_id',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='stripe_client_secret',
        ),
        migrations.AlterField(
            model_name='payment',
            name='method',
            field=models.CharField(
                choices=[('nequi', 'Nequi')],
                default='nequi',
                max_length=10,
                verbose_name='método',
            ),
        ),
    ]