# Generated by Django 3.2.4 on 2021-06-09 08:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    # replaces = [('applyment', '0001_initial'), ('applyment', '0002_auto_20210331_0823'), ('applyment', '0003_auto_20210402_0738'), ('applyment', '0004_delete_applyservice')]

    dependencies = [
        ('service', '0001_squashed_0006_userquota_deleted_squashed_0009_rename_data_center_applyvmservice_organization'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplyQuota',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='申请时间')),
                ('approve_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='审批时间')),
                ('status', models.CharField(choices=[('wait', '待审批'), ('pending', '审批中'), ('pass', '审批通过'), ('reject', '拒绝'), ('cancel', '取消申请')], default='wait', max_length=16, verbose_name='状态')),
                ('private_ip', models.IntegerField(default=0, verbose_name='总私网IP数')),
                ('public_ip', models.IntegerField(default=0, verbose_name='总公网IP数')),
                ('vcpu', models.IntegerField(default=0, verbose_name='总CPU核数')),
                ('ram', models.IntegerField(default=0, verbose_name='总内存大小(MB)')),
                ('disk_size', models.IntegerField(default=0, verbose_name='总硬盘大小(GB)')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_apply_quota_set', to=settings.AUTH_USER_MODEL, verbose_name='申请用户')),
                ('approve_user', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approve_apply_quota', to=settings.AUTH_USER_MODEL, verbose_name='审批人')),
                ('company', models.CharField(blank=True, default='', max_length=64, verbose_name='申请人单位')),
                ('contact', models.CharField(blank=True, default='', max_length=64, verbose_name='联系方式')),
                ('purpose', models.CharField(blank=True, default='', max_length=255, verbose_name='用途')),
                ('user_quota', models.OneToOneField(default=None, help_text='资源配额申请审批通过后生成的对应的用户资源配额', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='apply_quota', to='service.userquota', verbose_name='用户资源配额')),
                ('deleted', models.BooleanField(default=False, help_text='选中为删除', verbose_name='删除')),
                ('duration_days', models.IntegerField(blank=True, default=0, help_text='审批通过后到配额到期期间的时长，单位天', verbose_name='申请使用时长(天)')),
                ('service', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, related_name='service_apply_quota_set', to='service.serviceconfig', verbose_name='服务')),
            ],
            options={
                'ordering': ['-creation_time'],
                'verbose_name': '用户资源申请',
                'verbose_name_plural': '用户资源申请',
            },
        ),
    ]
