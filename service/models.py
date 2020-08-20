from django.db import models
from django.utils.translation import gettext_lazy as _


app_name = 'service'


class ServiceConfig(models.Model):
    """
    资源服务接入配置
    """
    SERVICE_EVCLOUD = 0
    SERVICE_OPENSTACK = 1
    SERVICE_TYPE_CHOICES = (
        (SERVICE_EVCLOUD, 'EVCloud'),
        (SERVICE_OPENSTACK, 'OpenStack'),
    )

    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name=_('服务名称'))
    region_id = models.CharField(max_length=128, default='', blank=True, verbose_name=_('服务区域/分中心ID'))
    service_type = models.SmallIntegerField(choices=SERVICE_TYPE_CHOICES, default=SERVICE_EVCLOUD, verbose_name=_('服务平台类型'))
    endpoint_url = models.CharField(max_length=300, verbose_name=_('服务地址url'), help_text='http(s)://{hostname}:{port}/')
    api_version = models.CharField(max_length=64, default='v3', verbose_name=_('API版本'), help_text=_('预留，主要EVCloud使用'))
    username = models.CharField(max_length=128, verbose_name=_('用户名'), help_text=_('用于此服务认证的用户名'))
    password = models.CharField(max_length=128, verbose_name=_('密码'))
    add_time = models.DateTimeField(auto_now_add=True, verbose_name=_('添加时间'))
    active = models.BooleanField(default=True, verbose_name=_('可用状态'), help_text=_('指示此配置是否可用'))
    remarks = models.CharField(max_length=255, default='', blank=True, verbose_name=_('备注'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('服务接入配置')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# class ServiceQuotaLimit(models.Model):
#     """
#     服务中心资源配额和限制
#     """
#     id = models.IntegerField(verbose_name='ID', primary_key=True)
#     service =

