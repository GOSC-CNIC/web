# Generated by Django 2.2.16 on 2020-09-22 02:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service', '0002_auto_20200922_0253'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplyService',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='申请时间')),
                ('approve_time', models.DateTimeField(auto_now_add=True, verbose_name='审批时间')),
                ('status', models.SmallIntegerField(choices=[(1, '待审批'), (2, '审批通过'), (3, '拒绝')], default=1, verbose_name='状态')),
                ('name', models.CharField(max_length=255, verbose_name='服务名称')),
                ('region_id', models.CharField(blank=True, default='', max_length=128, verbose_name='服务区域/分中心ID')),
                ('service_type', models.SmallIntegerField(choices=[(0, 'EVCloud'), (1, 'OpenStack')], default=0, verbose_name='服务平台类型')),
                ('endpoint_url', models.CharField(help_text='http(s)://{hostname}:{port}/', max_length=255, unique=True, verbose_name='服务地址url')),
                ('api_version', models.CharField(default='v3', help_text='预留，主要EVCloud使用', max_length=64, verbose_name='API版本')),
                ('username', models.CharField(help_text='用于此服务认证的用户名', max_length=128, verbose_name='用户名')),
                ('password', models.CharField(max_length=128, verbose_name='密码')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('need_vpn', models.BooleanField(default=True, verbose_name='是否需要VPN')),
                ('vpn_endpoint_url', models.CharField(help_text='http(s)://{hostname}:{port}/', max_length=255, verbose_name='VPN服务地址url')),
                ('vpn_api_version', models.CharField(default='v3', max_length=64, verbose_name='VPN API版本')),
                ('vpn_username', models.CharField(help_text='用于VPN服务认证的用户名', max_length=128, verbose_name='用户名')),
                ('vpn_password', models.CharField(max_length=128, verbose_name='密码')),
                ('data_center', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='service.DataCenter', verbose_name='数据中心')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
        ),
        migrations.CreateModel(
            name='ApplyQuota',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='申请时间')),
                ('approve_time', models.DateTimeField(auto_now_add=True, verbose_name='审批时间')),
                ('status', models.SmallIntegerField(choices=[(1, '待审批'), (2, '审批通过'), (3, '拒绝')], default=1, verbose_name='状态')),
                ('private_ip', models.IntegerField(default=0, verbose_name='总私网IP数')),
                ('public_ip', models.IntegerField(default=0, verbose_name='总公网IP数')),
                ('vcpu', models.IntegerField(default=0, verbose_name='总CPU核数')),
                ('ram', models.IntegerField(default=0, verbose_name='总内存大小(MB)')),
                ('disk_size', models.IntegerField(default=0, verbose_name='总硬盘大小(GB)')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
        ),
    ]