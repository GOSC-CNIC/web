# Generated by Django 3.2.4 on 2021-06-29 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0002_auto_20210617_0751'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='classification',
            field=models.CharField(choices=[('personal', '个人的'), ('vo', 'VO组的')], default='personal', help_text='标识配额属于申请者个人的，还是vo组的', max_length=16, verbose_name='资源配额归属类型'),
        ),
        migrations.AddField(
            model_name='serverarchive',
            name='classification',
            field=models.CharField(choices=[('personal', '个人的'), ('vo', 'VO组的')], default='personal', help_text='标识配额属于申请者个人的，还是vo组的', max_length=16, verbose_name='资源配额归属类型'),
        ),
    ]
