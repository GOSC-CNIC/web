from datetime import timedelta

from django.db import models
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

from utils.model import UuidModel
from utils.crypto import Encryptor
from core import errors
from vo.models import VirtualOrganization


User = get_user_model()
app_name = 'service'


def get_encryptor():
    return Encryptor(key=settings.SECRET_KEY)


class DataCenter(UuidModel):
    STATUS_ENABLE = 1
    STATUS_DISABLE = 2
    CHOICE_STATUS = (
        (STATUS_ENABLE, _('开启状态')),
        (STATUS_DISABLE, _('关闭状态'))
    )

    name = models.CharField(verbose_name=_('名称'), max_length=255)
    name_en = models.CharField(verbose_name=_('英文名称'), max_length=255, default='')
    abbreviation = models.CharField(verbose_name=_('简称'), max_length=64, default='')
    independent_legal_person = models.BooleanField(verbose_name=_('是否独立法人单位'), default=True)
    country = models.CharField(verbose_name=_('国家/地区'), max_length=128, default='')
    city = models.CharField(verbose_name=_('城市'), max_length=128, default='')
    postal_code = models.CharField(verbose_name=_('邮政编码'), max_length=32, default='')
    address = models.CharField(verbose_name=_('单位地址'), max_length=256, default='')

    endpoint_vms = models.CharField(max_length=255, verbose_name=_('云主机服务地址url'),
                                    null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    endpoint_object = models.CharField(max_length=255, verbose_name=_('存储服务地址url'),
                                       null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    endpoint_compute = models.CharField(max_length=255, verbose_name=_('计算服务地址url'),
                                        null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    endpoint_monitor = models.CharField(max_length=255, verbose_name=_('检测报警服务地址url'),
                                        null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    creation_time = models.DateTimeField(verbose_name=_('创建时间'), null=True, blank=True, default=None)
    status = models.SmallIntegerField(verbose_name=_('服务状态'), choices=CHOICE_STATUS, default=STATUS_ENABLE)
    desc = models.CharField(verbose_name=_('描述'), blank=True, max_length=255)

    logo_url = models.CharField(verbose_name=_('LOGO url'), max_length=256,
                                blank=True, default='')
    certification_url = models.CharField(verbose_name=_('机构认证代码url'), max_length=256,
                                         blank=True, default='')

    class Meta:
        ordering = ['creation_time']
        verbose_name = _('机构')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ServiceConfig(UuidModel):
    """
    资源服务接入配置
    """
    class ServiceType(models.TextChoices):
        EVCLOUD = 'evcloud', 'EVCloud'
        OPENSTACK = 'openstack', 'OpenStack'
        VMWARE = 'vmware', 'VMware'

    class Status(models.TextChoices):
        ENABLE = 'enable', _('服务中')
        DISABLE = 'disable', _('停止服务')
        DELETED = 'deleted', _('删除')

    data_center = models.ForeignKey(to=DataCenter, null=True, on_delete=models.SET_NULL,
                                    related_name='service_set', verbose_name=_('数据中心'))
    name = models.CharField(max_length=255, verbose_name=_('服务名称'))
    name_en = models.CharField(verbose_name=_('服务英文名称'), max_length=255, default='')
    region_id = models.CharField(max_length=128, default='', blank=True, verbose_name=_('服务区域/分中心ID'))
    service_type = models.CharField(max_length=32, choices=ServiceType.choices, default=ServiceType.EVCLOUD,
                                    verbose_name=_('服务平台类型'))
    endpoint_url = models.CharField(max_length=255, verbose_name=_('服务地址url'), unique=True,
                                    help_text='http(s)://{hostname}:{port}/')
    api_version = models.CharField(max_length=64, default='v3', verbose_name=_('API版本'),
                                   help_text=_('预留，主要EVCloud使用'))
    username = models.CharField(max_length=128, verbose_name=_('用户名'), help_text=_('用于此服务认证的用户名'))
    password = models.CharField(max_length=255, verbose_name=_('密码'))
    add_time = models.DateTimeField(auto_now_add=True, verbose_name=_('添加时间'))
    status = models.CharField(verbose_name=_('服务状态'), max_length=32, choices=Status.choices, default=Status.ENABLE)
    remarks = models.CharField(max_length=255, default='', blank=True, verbose_name=_('备注'))
    need_vpn = models.BooleanField(verbose_name=_('是否需要VPN'), default=True)
    vpn_endpoint_url = models.CharField(max_length=255, blank=True, default='', verbose_name=_('VPN服务地址url'),
                                        help_text='http(s)://{hostname}:{port}/')
    vpn_api_version = models.CharField(max_length=64, blank=True, default='v3', verbose_name=_('VPN服务API版本'),
                                       help_text=_('预留，主要EVCloud使用'))
    vpn_username = models.CharField(max_length=128, blank=True, default='', verbose_name=_('VPN服务用户名'),
                                    help_text=_('用于此服务认证的用户名'))
    vpn_password = models.CharField(max_length=255, blank=True, default='', verbose_name=_('VPN服务密码'))
    extra = models.CharField(max_length=1024, blank=True, default='', verbose_name=_('其他配置'), help_text=_('json格式'))
    users = models.ManyToManyField(to=User, verbose_name=_('用户'), blank=True, related_name='service_set')

    contact_person = models.CharField(verbose_name=_('联系人名称'), max_length=128,
                                      blank=True, default='')
    contact_email = models.EmailField(verbose_name=_('联系人邮箱'), blank=True, default='')
    contact_telephone = models.CharField(verbose_name=_('联系人电话'), max_length=16,
                                         blank=True, default='')
    contact_fixed_phone = models.CharField(verbose_name=_('联系人固定电话'), max_length=16,
                                           blank=True, default='')
    contact_address = models.CharField(verbose_name=_('联系人地址'), max_length=256,
                                       blank=True, default='')
    logo_url = models.CharField(verbose_name=_('LOGO url'), max_length=256,
                                blank=True, default='')

    class Meta:
        ordering = ['-add_time']
        verbose_name = _('服务接入配置')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def raw_password(self):
        """
        :return:
            str     # success
            None    # failed, invalid encrypted password
        """
        encryptor = get_encryptor()
        try:
            return encryptor.decrypt(self.password)
        except encryptor.InvalidEncrypted as e:
            return None

    def set_password(self, raw_password: str):
        encryptor = get_encryptor()
        self.password = encryptor.encrypt(raw_password)

    def raw_vpn_password(self):
        """
        :return:
            str     # success
            None    # failed, invalid encrypted password
        """
        encryptor = get_encryptor()
        try:
            return encryptor.decrypt(self.vpn_password)
        except encryptor.InvalidEncrypted as e:
            return None

    def set_vpn_password(self, raw_password: str):
        encryptor = get_encryptor()
        self.vpn_password = encryptor.encrypt(raw_password)

    def is_need_vpn(self):
        return self.need_vpn

    def check_vpn_config(self):
        """
        检查vpn配置
        :return:
        """
        if not self.is_need_vpn():
            return True

        if self.service_type == self.ServiceType.EVCLOUD:
            return True

        if not self.vpn_endpoint_url or not self.vpn_password or not self.vpn_username:
            return False

        return True

    def user_has_perm(self, user):
        """
        用户是否有访问此服务的管理权限

        :param user: 用户
        :return:
            True    # has
            False   # no
        """
        if not user or not user.id:
            return False

        return self.users.filter(id=user.id).exists()


class ServiceQuotaBase(UuidModel):
    """
    数据中心接入服务的资源配额基类
    """
    private_ip_total = models.IntegerField(verbose_name=_('总私网IP数'), default=0)
    private_ip_used = models.IntegerField(verbose_name=_('已用私网IP数'), default=0)
    public_ip_total = models.IntegerField(verbose_name=_('总公网IP数'), default=0)
    public_ip_used = models.IntegerField(verbose_name=_('已用公网IP数'), default=0)
    vcpu_total = models.IntegerField(verbose_name=_('总CPU核数'), default=0)
    vcpu_used = models.IntegerField(verbose_name=_('已用CPU核数'), default=0)
    ram_total = models.IntegerField(verbose_name=_('总内存大小(MB)'), default=0)
    ram_used = models.IntegerField(verbose_name=_('已用内存大小(MB)'), default=0)
    disk_size_total = models.IntegerField(verbose_name=_('总硬盘大小(GB)'), default=0)
    disk_size_used = models.IntegerField(verbose_name=_('已用硬盘大小(GB)'), default=0)
    creation_time = models.DateTimeField(verbose_name=_('创建时间'), null=True, blank=True, auto_now_add=True)
    enable = models.BooleanField(verbose_name=_('有效状态'), default=True,
                                 help_text=_('选中，资源配额生效；未选中，无法申请分中心资源'))

    class Meta:
        abstract = True


class ServicePrivateQuota(ServiceQuotaBase):
    """
    数据中心接入服务的私有资源配额和限制
    """
    service = models.OneToOneField(to=ServiceConfig, null=True, on_delete=models.SET_NULL,
                                   related_name='service_private_quota', verbose_name=_('接入服务'))

    class Meta:
        db_table = 'service_private_quota'
        ordering = ['-creation_time']
        verbose_name = _('接入服务的私有资源配额')
        verbose_name_plural = verbose_name


class ServiceShareQuota(ServiceQuotaBase):
    """
    接入服务的分享资源配额和限制
    """
    service = models.OneToOneField(to=ServiceConfig, null=True, on_delete=models.SET_NULL,
                                   related_name='service_share_quota', verbose_name=_('接入服务'))

    class Meta:
        db_table = 'service_share_quota'
        ordering = ['-creation_time']
        verbose_name = _('接入服务的分享资源配额')
        verbose_name_plural = verbose_name


class UserQuota(UuidModel):
    """
    用户资源配额限制

    配额属于用户或者项目组
    """
    EXPIRATION_DAYS = 30    # 配额过期时长

    TAG_BASE = 1
    TAG_PROBATION = 2
    CHOICES_TAG = (
        (TAG_BASE, _('普通配额')),
        (TAG_PROBATION, _('试用配额'))
    )

    class Classification(models.TextChoices):
        PERSONAL = 'personal', _('个人的')
        VO = 'vo', _('VO组的')

    tag = models.SmallIntegerField(verbose_name=_('配额类型'), choices=CHOICES_TAG, default=TAG_BASE)
    user = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL, default=None,
                             related_name='user_quota', verbose_name=_('用户'))
    vo = models.ForeignKey(to=VirtualOrganization, null=True, on_delete=models.SET_NULL, default=None,
                           related_name='vo_quota_set', verbose_name=_('项目组'))
    service = models.ForeignKey(to=ServiceConfig, null=True, on_delete=models.SET_NULL,
                                related_name='service_quota', verbose_name=_('适用服务'))
    private_ip_total = models.IntegerField(verbose_name=_('总私网IP数'), default=0)
    private_ip_used = models.IntegerField(verbose_name=_('已用私网IP数'), default=0)
    public_ip_total = models.IntegerField(verbose_name=_('总公网IP数'), default=0)
    public_ip_used = models.IntegerField(verbose_name=_('已用公网IP数'), default=0)
    vcpu_total = models.IntegerField(verbose_name=_('总CPU核数'), default=0)
    vcpu_used = models.IntegerField(verbose_name=_('已用CPU核数'), default=0)
    ram_total = models.IntegerField(verbose_name=_('总内存大小(MB)'), default=0)
    ram_used = models.IntegerField(verbose_name=_('已用内存大小(MB)'), default=0)
    disk_size_total = models.IntegerField(verbose_name=_('总硬盘大小(GB)'), default=0)
    disk_size_used = models.IntegerField(verbose_name=_('已用硬盘大小(GB)'), default=0)
    creation_time = models.DateTimeField(verbose_name=_('创建时间'), null=True, blank=True, auto_now_add=True)
    expiration_time = models.DateTimeField(verbose_name=_('过期时间'), null=True, blank=True, default=None,
                                           help_text=_('过期后不能再用于创建资源'))
    is_email = models.BooleanField(verbose_name=_('是否邮件通知'), default=False, help_text=_('是否邮件通知用户配额即将到期'))
    deleted = models.BooleanField(verbose_name=_('删除'), default=False)
    duration_days = models.IntegerField(verbose_name=_('资源使用时长'), blank=True, default=365,
                                        help_text=_('使用此配额创建的资源的有效使用时长'))
    classification = models.CharField(verbose_name=_('资源配额归属类型'), max_length=16,
                                      choices=Classification.choices, default=Classification.PERSONAL,
                                      help_text=_('标识配额属于申请者个人的，还是vo组的'))

    class Meta:
        db_table = 'user_quota'
        ordering = ['-creation_time']
        verbose_name = _('用户资源配额')
        verbose_name_plural = verbose_name

    def __str__(self):
        values = []
        if self.vcpu_total > 0:
            values.append(f'vCPU: {self.vcpu_total}')
        if self.ram_total > 0:
            values.append(f'RAM: {self.ram_total}Mb')
        if self.disk_size_total > 0:
            values.append(f'Disk: {self.disk_size_total}Gb')
        if self.public_ip_total > 0:
            values.append(f'PublicIP: {self.public_ip_total}')
        if self.private_ip_total > 0:
            values.append(f'PrivateIP: {self.private_ip_total}')
        if self.duration_days > 0:
            values.append(f'Days: {self.duration_days}')

        if values:
            s = ', '.join(values)
        else:
            s = 'vCPU: 0, RAM:0 Mb, 0, 0, 0'

        return f'[{self.get_tag_display()}]({s})'

    @property
    def display(self):
        return self.__str__()

    @property
    def vcpu_free_count(self):
        return self.vcpu_total - self.vcpu_used

    @property
    def ram_free_count(self):
        return self.ram_total - self.ram_used

    @property
    def disk_free_size(self):
        return self.disk_size_total - self.disk_size_used

    @property
    def public_ip_free_count(self):
        return self.public_ip_total - self.public_ip_used

    @property
    def private_ip_free_count(self):
        return self.private_ip_total - self.private_ip_used

    @property
    def all_ip_count(self):
        return self.private_ip_total + self.public_ip_total

    def is_expire_now(self):
        """
        资源配额现在是否过期
        :return:
            True    # 过期
            False   # 未过期
        """
        if not self.expiration_time:        # 未设置过期时间
            return False

        now = timezone.now()
        ts_now = now.timestamp()
        ts_expire = self.expiration_time.timestamp()
        if (ts_now + 60) > ts_expire:  # 1分钟内算过期
            return True

        return False


class ApplyOrganization(UuidModel):
    """
    数据中心/机构申请
    """
    class Status(models.TextChoices):
        WAIT = 'wait', '待审批'
        CANCEL = 'cancel', _('取消申请')
        PENDING = 'pending', '审批中'
        REJECT = 'reject', '拒绝'
        PASS = 'pass', '通过'

    name = models.CharField(verbose_name=_('名称'), max_length=255)
    name_en = models.CharField(verbose_name=_('英文名称'), max_length=255, default='')
    abbreviation = models.CharField(verbose_name=_('简称'), max_length=64, default='')
    independent_legal_person = models.BooleanField(verbose_name=_('是否独立法人单位'), default=True)
    country = models.CharField(verbose_name=_('国家/地区'), max_length=128, default='')
    city = models.CharField(verbose_name=_('城市'), max_length=128, default='')
    postal_code = models.CharField(verbose_name=_('邮政编码'), max_length=32, default='')
    address = models.CharField(verbose_name=_('单位地址'), max_length=256, default='')

    endpoint_vms = models.CharField(max_length=255, verbose_name=_('云主机服务地址url'),
                                    null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    endpoint_object = models.CharField(max_length=255, verbose_name=_('存储服务地址url'),
                                       null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    endpoint_compute = models.CharField(max_length=255, verbose_name=_('计算服务地址url'),
                                        null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    endpoint_monitor = models.CharField(max_length=255, verbose_name=_('检测报警服务地址url'),
                                        null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    creation_time = models.DateTimeField(verbose_name=_('创建时间'), null=True, blank=True, auto_now_add=True)
    status = models.CharField(verbose_name=_('状态'), max_length=16,
                              choices=Status.choices, default=Status.WAIT)
    desc = models.CharField(verbose_name=_('描述'), blank=True, max_length=255)
    data_center = models.OneToOneField(to=DataCenter, null=True, on_delete=models.SET_NULL,
                                       related_name='apply_data_center', blank=True,
                                       default=None, verbose_name=_('机构'),
                                       help_text=_('机构加入申请审批通过后对应的机构'))

    logo_url = models.CharField(verbose_name=_('LOGO url'), max_length=256,
                                blank=True, default='')
    certification_url = models.CharField(verbose_name=_('机构认证代码url'), max_length=256,
                                         blank=True, default='')

    user = models.ForeignKey(verbose_name=_('申请用户'), to=User, null=True, on_delete=models.SET_NULL)
    deleted = models.BooleanField(verbose_name=_('删除'), default=False)

    class Meta:
        db_table = 'organization_apply'
        ordering = ['creation_time']
        verbose_name = _('机构加入申请')
        verbose_name_plural = verbose_name

    def is_pass(self):
        return self.status == self.Status.PASS

    def __str__(self):
        return self.name

    def do_pass_apply(self) -> DataCenter:
        organization = DataCenter()
        organization.name = self.name
        organization.name_en = self.name_en
        organization.abbreviation = self.abbreviation
        organization.independent_legal_person = self.independent_legal_person
        organization.country = self.country
        organization.city = self.city
        organization.postal_code = self.postal_code
        organization.address = self.address
        organization.endpoint_vms = self.endpoint_vms
        organization.endpoint_object = self.endpoint_object
        organization.endpoint_compute = self.endpoint_compute
        organization.endpoint_monitor = self.endpoint_monitor
        organization.desc = self.desc
        organization.logo_url = self.logo_url
        organization.certification_url = self.certification_url

        with transaction.atomic():
            organization.save()
            self.status = self.Status.PASS
            self.data_center = organization
            self.save(update_fields=['status', 'data_center'])

        return organization


class ApplyVmService(UuidModel):
    """
    服务接入申请
    """
    class Status(models.TextChoices):
        WAIT = 'wait', _('待审核')
        CANCEL = 'cancel', _('取消申请')
        PENDING = 'pending', _('审核中')
        FIRST_PASS = 'first_pass', _('初审通过')
        FIRST_REJECT = 'first_reject', _('初审拒绝')
        TEST_FAILED = 'test_failed', _('测试未通过')
        TEST_PASS = 'test_pass', _('测试通过')
        REJECT = 'reject', _('拒绝')
        PASS = 'pass', _('通过')

    class ServiceType(models.TextChoices):
        EVCLOUD = 'evcloud', 'EVCloud'
        OPENSTACK = 'openstack', 'OpenStack'
        VMWARE = 'vmware', 'VMware'

    user = models.ForeignKey(verbose_name=_('申请用户'), to=User, null=True, on_delete=models.SET_NULL)
    creation_time = models.DateTimeField(verbose_name=_('申请时间'), auto_now_add=True)
    approve_time = models.DateTimeField(verbose_name=_('审批时间'), auto_now_add=True)
    status = models.CharField(verbose_name=_('状态'), max_length=16,
                              choices=Status.choices, default=Status.WAIT)

    organization = models.ForeignKey(to=DataCenter, null=True, on_delete=models.SET_NULL, verbose_name=_('数据中心'))
    longitude = models.FloatField(verbose_name=_('经度'), blank=True, default=0)
    latitude = models.FloatField(verbose_name=_('纬度'), blank=True, default=0)
    name = models.CharField(max_length=255, verbose_name=_('服务名称'))
    name_en = models.CharField(verbose_name=_('英文名称'), max_length=255, default='')
    region = models.CharField(max_length=128, default='', blank=True, verbose_name=_('服务区域'),
                              help_text='OpenStack服务区域名称,EVCloud分中心ID')
    service_type = models.CharField(choices=ServiceType.choices, default=ServiceType.EVCLOUD,
                                    max_length=16, verbose_name=_('服务平台类型'))
    endpoint_url = models.CharField(max_length=255, verbose_name=_('服务地址url'), unique=True,
                                    help_text='http(s)://{hostname}:{port}/')
    api_version = models.CharField(max_length=64, default='v3', verbose_name=_('API版本'), help_text=_('预留，主要EVCloud使用'))
    username = models.CharField(max_length=128, verbose_name=_('用户名'), help_text=_('用于此服务认证的用户名'))
    password = models.CharField(max_length=255, verbose_name=_('密码'))
    project_name = models.CharField(
        verbose_name='Project Name', max_length=128, blank=True, default='',
        help_text='only required when OpenStack')
    project_domain_name = models.CharField(
        verbose_name='Project Domain Name', blank=True, max_length=128,
        help_text='only required when OpenStack', default='')
    user_domain_name = models.CharField(
        verbose_name='User Domain Name', max_length=128, blank=True, default='',
        help_text='only required when OpenStack')
    remarks = models.CharField(max_length=255, default='', blank=True, verbose_name=_('备注'))
    need_vpn = models.BooleanField(verbose_name=_('是否需要VPN'), default=True)

    vpn_endpoint_url = models.CharField(max_length=255, verbose_name=_('VPN服务地址url'),
                                        help_text='http(s)://{hostname}:{port}/')
    vpn_api_version = models.CharField(max_length=64, default='v3', verbose_name=_('VPN API版本'))
    vpn_username = models.CharField(max_length=128, verbose_name=_('用户名'), help_text=_('用于VPN服务认证的用户名'))
    vpn_password = models.CharField(max_length=255, verbose_name=_('密码'))
    service = models.OneToOneField(to=ServiceConfig, null=True, on_delete=models.SET_NULL, related_name='apply_service',
                                   default=None, verbose_name=_('接入服务'),
                                   help_text=_('服务接入申请审批通过后生成的对应的接入服务'))
    deleted = models.BooleanField(verbose_name=_('删除'), default=False)

    contact_person = models.CharField(verbose_name=_('联系人'), max_length=128,
                                      blank=True, default='')
    contact_email = models.EmailField(verbose_name=_('联系人邮箱'), blank=True, default='')
    contact_telephone = models.CharField(verbose_name=_('联系人电话'), max_length=16,
                                         blank=True, default='')
    contact_fixed_phone = models.CharField(verbose_name=_('联系人固定电话'), max_length=16,
                                           blank=True, default='')
    contact_address = models.CharField(verbose_name=_('联系人地址'), max_length=256,
                                       blank=True, default='')
    logo_url = models.CharField(verbose_name=_('LOGO url'), max_length=256,
                                blank=True, default='')

    class Meta:
        db_table = 'vm_service_apply'
        ordering = ['-creation_time']
        verbose_name = _('VM服务接入申请')
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'ApplyService(name={self.name})'

    def raw_password(self):
        """
        :return:
            str     # success
            None    # failed, invalid encrypted password
        """
        encryptor = get_encryptor()
        try:
            return encryptor.decrypt(self.password)
        except encryptor.InvalidEncrypted as e:
            return None

    def set_password(self, raw_password: str):
        encryptor = get_encryptor()
        self.password = encryptor.encrypt(raw_password)

    def raw_vpn_password(self):
        """
        :return:
            str     # success
            None    # failed, invalid encrypted password
        """
        encryptor = get_encryptor()
        try:
            return encryptor.decrypt(self.vpn_password)
        except encryptor.InvalidEncrypted as e:
            return None

    def set_vpn_password(self, raw_password: str):
        encryptor = get_encryptor()
        self.vpn_password = encryptor.encrypt(raw_password)

    def convert_to_service(self) -> ServiceConfig:
        """
        申请转为对应的ServiceConfig对象
        :return:
        """
        if not self.organization_id:
            raise errors.NoCenterBelongToError()

        service = ServiceConfig()
        service.data_center_id = self.organization_id
        service.name = self.name
        service.name_en = self.name_en
        service.region_id = self.region
        service.service_type = self.service_type
        service.endpoint_url = self.endpoint_url
        service.api_version = self.api_version
        service.username = self.username
        service.set_password(self.raw_password())
        service.remarks = self.remarks
        service.need_vpn = self.need_vpn
        service.vpn_endpoint_url = self.vpn_endpoint_url
        service.vpn_api_version = self.vpn_api_version
        service.vpn_username = self.vpn_username
        service.set_vpn_password(self.raw_vpn_password())
        service.contact_person = self.contact_person
        service.contact_email = self.contact_email
        service.contact_telephone = self.contact_telephone
        service.contact_fixed_phone = self.contact_fixed_phone
        service.contact_address = self.contact_address
        service.logo_url = self.logo_url
        return service

    def do_pass_apply(self) -> ServiceConfig:
        service = self.convert_to_service()
        with transaction.atomic():
            service.save()
            service.users.add(self.user)        # 服务管理员
            self.status = self.Status.PASS
            self.service = service
            self.approve_time = timezone.now()
            self.save(update_fields=['status', 'service', 'approve_time'])

        return service


class ApplyQuota(UuidModel):
    """
    用户资源申请
    """
    STATUS_WAIT = 'wait'
    STATUS_PENDING = 'pending'
    STATUS_PASS = 'pass'
    STATUS_REJECT = 'reject'
    STATUS_CANCEL = 'cancel'
    CHOICE_STATUS = (
        (STATUS_WAIT, _('待审批')),
        (STATUS_PENDING, _('审批中')),
        (STATUS_PASS, _('审批通过')),
        (STATUS_REJECT, _('拒绝')),
        (STATUS_CANCEL, _('取消申请')),
    )
    LIST_STATUS = [STATUS_WAIT, STATUS_PENDING, STATUS_PASS, STATUS_REJECT, STATUS_CANCEL]

    class Classification(models.TextChoices):
        PERSONAL = 'personal', _('个人的')
        VO = 'vo', _('VO组的')

    service = models.ForeignKey(verbose_name=_('服务'), to=ServiceConfig, default='',
                                on_delete=models.DO_NOTHING, related_name='service_apply_quota_set')
    user = models.ForeignKey(verbose_name=_('申请用户'), to=User, null=True,
                             on_delete=models.SET_NULL, related_name='user_apply_quota_set')
    approve_user = models.ForeignKey(verbose_name=_('审批人'), to=User, null=True, on_delete=models.SET_NULL,
                                     related_name='approve_apply_quota', default=None)
    creation_time = models.DateTimeField(verbose_name=_('申请时间'), auto_now_add=True)
    approve_time = models.DateTimeField(verbose_name=_('审批时间'), null=True, blank=True, default=None)
    status = models.CharField(verbose_name=_('状态'), max_length=16, choices=CHOICE_STATUS, default=STATUS_WAIT)

    private_ip = models.IntegerField(verbose_name=_('总私网IP数'), default=0)
    public_ip = models.IntegerField(verbose_name=_('总公网IP数'), default=0)
    vcpu = models.IntegerField(verbose_name=_('总CPU核数'), default=0)
    ram = models.IntegerField(verbose_name=_('总内存大小(MB)'), default=0)
    disk_size = models.IntegerField(verbose_name=_('总硬盘大小(GB)'), default=0)

    duration_days = models.IntegerField(verbose_name=_('申请使用时长(天)'), blank=True, default=0,
                                        help_text=_('审批通过后到配额到期期间的时长，单位天'))
    company = models.CharField(verbose_name=_('申请人单位'), max_length=64, blank=True, default='')
    contact = models.CharField(verbose_name=_('联系方式'), max_length=64, blank=True, default='')
    purpose = models.CharField(verbose_name=_('用途'), max_length=255, blank=True, default='')
    user_quota = models.OneToOneField(to=UserQuota, null=True, on_delete=models.SET_NULL, related_name='apply_quota',
                                      default=None, verbose_name=_('用户资源配额'),
                                      help_text=_('资源配额申请审批通过后生成的对应的用户资源配额'))
    deleted = models.BooleanField(verbose_name=_('删除'), default=False, help_text=_('选中为删除'))
    classification = models.CharField(verbose_name=_('资源配额归属类型'), max_length=16,
                                      choices=Classification.choices, default=Classification.PERSONAL,
                                      help_text=_('标识配额属于申请者个人的，还是vo组的'))
    vo = models.ForeignKey(to=VirtualOrganization, null=True, on_delete=models.SET_NULL, default=None,
                           related_name='vo_apply_quota_set', verbose_name=_('项目组'))

    class Meta:
        db_table = 'applyment_applyquota'     # 'apply_vm_quota'
        ordering = ['-creation_time']
        verbose_name = _('用户资源配额申请')
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'ApplyQuota(vcpu={self.vcpu}, ram={self.ram}Mb, disk_size={self.disk_size}Gb, ' \
               f'status={self.get_status_display()})'

    def is_wait_status(self):
        """
        是否是待审批状态
        :return:
            True
            False
        """
        return self.status == self.STATUS_WAIT

    def is_pending_status(self):
        """
        是否是审批中状态
        :return:
            True
            False
        """
        return self.status == self.STATUS_PENDING

    def is_cancel_status(self):
        """
        是否是已取消状态
        :return:
            True
            False
        """
        return self.status == self.STATUS_CANCEL

    def set_pending(self, user):
        """
        挂起申请
        :return:
            True    # success
            False   # failed
        """
        if not self.is_wait_status():
            return False

        self.status = self.STATUS_PENDING
        self.approve_user = user
        self.approve_time = timezone.now()
        self.save(update_fields=['status', 'approve_time', 'approve_user'])
        return True

    def set_reject(self, user):
        """
        拒绝申请
        :return:
            True    # success
            False   # failed
        """
        if not self.is_pending_status():
            return False

        self.status = self.STATUS_REJECT
        self.approve_user = user
        self.approve_time = timezone.now()
        self.save(update_fields=['status', 'approve_time', 'approve_user'])
        return True

    def set_pass(self, user, quota):
        """
        通过申请
        :return:
            True    # success
            False   # failed
        """
        if not self.is_pending_status():
            return False

        self.status = self.STATUS_PASS
        self.approve_user = user
        self.approve_time = timezone.now()
        self.user_quota = quota
        self.save(update_fields=['status', 'approve_time', 'approve_user', 'user_quota'])
        return True

    def set_cancel(self):
        """
        取消申请
        :return:
            True    # success
            False   # failed
        """
        if not self.is_wait_status():
            return False

        self.status = self.STATUS_CANCEL
        self.save(update_fields=['status'])
        return True

    def do_pass(self, user):
        """
        通过申请处理
        """
        quota = UserQuota()
        quota.user = self.user
        quota.service = self.service
        quota.private_ip_total = self.private_ip
        quota.public_ip_total = self.public_ip
        quota.vcpu_total = self.vcpu
        quota.ram_total = self.ram
        quota.disk_size_total = self.disk_size
        quota.expiration_time = timezone.now() + timedelta(days=UserQuota.EXPIRATION_DAYS)
        quota.duration_days = self.duration_days
        if self.classification == self.Classification.PERSONAL:
            quota.classification = quota.Classification.PERSONAL
            quota.vo = None
        else:
            quota.classification = quota.Classification.VO
            quota.vo_id = self.vo_id

        with transaction.atomic():
            quota.save()
            self.set_pass(user=user, quota=quota)

        return quota

    def do_soft_delete(self):
        """
        软删除申请记录
        :return:
            True    # success
        """
        self.deleted = True
        self.save(update_fields=['deleted'])
        return True
