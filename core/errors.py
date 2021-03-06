from rest_framework import exceptions as drf_exceptions


class Error(Exception):
    default_message = 'We encountered an internal error. Please try again.'
    default_code = 'InternalError'
    default_status_code = 500

    def __init__(self, message: str = '', code: str = '', status_code=None, extend_msg=''):
        """
        :param message: 错误描述
        :param code: 错误代码
        :param status_code: HTTP状态码
        :param extend_msg: 扩展错误描述的信息，追加到message后面
        """
        self.message = message if message else self.default_message
        self.code = code if code else self.default_code
        self.status_code = self.default_status_code if status_code is None else status_code
        if extend_msg:
            self.message += '&&' + extend_msg

    def __repr__(self):
        return f'{type(self)}(message={self.message}, code={self.code}, status_code={self.status_code})'

    def __str__(self):
        return self.message

    def detail_str(self):
        return self.__repr__()

    def err_data(self):
        return {
            'code': self.code,
            'message': self.message
        }

    @classmethod
    def from_error(cls, err):
        if isinstance(err, Error):
            return cls(message=err.message, code=err.code, status_code=err.status_code)

        return cls(message=str(err))


class BadRequestError(Error):
    default_message = "bad request."
    default_code = "BadRequest"
    default_status_code = 400


class QuotaError(Error):
    pass


class NoSuchQuotaError(QuotaError):
    default_message = "The specified quota does not exist."
    default_code = "NoSuchQuota"
    default_status_code = 404


class QuotaShortageError(QuotaError):
    """配额不足短缺"""
    default_message = "There are not enough resources to use."
    default_code = "QuotaShortage"
    default_status_code = 409


class QuotaOnlyIncreaseError(QuotaError):
    """配额只允许增加"""
    default_message = "The quota can only be increased."
    default_code = "QuotaOnlyIncrease"
    default_status_code = 409


class CenterApplyNotPassError(Error):
    default_message = '机构加入申请未通过'
    default_code = 'CenterApplyNotPass'
    default_status_code = 409


class DoNotKnowWhichCenterBelongToError(Error):
    default_message = '不确定归属于哪一个机构'
    default_code = 'DoNotKnowWhichCenterBelongTo'
    default_status_code = 409


class NoCenterBelongToError(Error):
    default_message = '没有归属的机构'
    default_code = 'NoCenterBelongTo'
    default_status_code = 409


class APIException(Error):
    pass


class BadRequest(APIException):
    default_message = 'BadRequest.'
    default_code = 'BadRequest'
    default_status_code = 400


class InvalidDigest(BadRequest):
    default_message = 'The Content-MD5 you specified is not valid.'
    default_code = 'InvalidDigest'
    default_status_code = 400


class BadDigest(BadRequest):
    default_message = 'The Content-MD5 you specified did not match what we received.'
    default_code = 'BadDigest'
    default_status_code = 400


class InvalidArgument(BadRequest):
    default_message = 'Invalid Argument.'
    default_code = 'InvalidArgument'


class NoFoundArgument(BadRequest):
    default_message = 'No Found Argument.'
    default_code = 'NoFoundArgument'


class AuthenticationFailed(APIException):
    default_message = 'Incorrect authentication credentials.'
    default_code = 'AuthenticationFailed'
    default_status_code = 401


class NotAuthenticated(APIException):
    default_message = 'Authentication credentials were not provided.'
    default_code = 'NotAuthenticated'
    default_status_code = 401


class InvalidJWT(APIException):
    default_message = 'Token is invalid or expired.'
    default_code = 'InvalidJWT'
    default_status_code = 401


class AccessDenied(APIException):
    default_message = 'Access Denied.'
    default_code = 'AccessDenied'
    default_status_code = 403


class NotFound(APIException):
    default_message = 'Not Found.'
    default_code = 'NotFound'
    default_status_code = 404


class ServerNotExist(NotFound):
    default_message = 'This server is not exist.'
    default_code = 'ServerNotExist'
    default_status_code = 404


class ServiceNotExist(NotFound):
    default_message = 'This service is not exist.'
    default_code = 'ServiceNotExist'


class OrganizationNotExists(NotFound):
    default_message = 'Organization is not exists.'
    default_code = 'OrganizationNotExists'


class OrganizationApplyNotExists(NotFound):
    default_message = 'The apply of Organization is not exists.'
    default_code = 'OrganizationApplyNotExists'


class NoSupportVPN(APIException):
    default_message = 'This service does not provide VPN support.'
    default_code = 'NoSupportVPN'
    default_status_code = 405


class MethodNotSupportInService(APIException):
    default_message = 'This method or business is not supported by this service center.'
    default_code = 'MethodNotSupportInService'
    default_status_code = 405


class ConflictError(APIException):
    default_message = '由于和被请求的资源的当前状态之间存在冲突，请求无法完成'
    default_code = 'Conflict'
    default_status_code = 409


class TooManyApply(ConflictError):
    default_message = '您已提交了多个申请，待审批，暂不能提交更多的申请'
    default_code = 'TooManyApply'


class ResourceNotCleanedUp(ConflictError):
    default_message = '资源未清理'
    default_code = 'ResourceNotCleanedUp'


def convert_to_error(err):
    if isinstance(err, Error):
        return err

    if not isinstance(err, drf_exceptions.APIException):
        return APIException.from_error(err)

    message = str(err)
    if isinstance(err, drf_exceptions.NotFound):
        return NotFound(message=message)
    if isinstance(err, drf_exceptions.PermissionDenied):
        return AccessDenied(message=message)
    if isinstance(err, drf_exceptions.NotAuthenticated):
        return AuthenticationFailed(message=message)

    return APIException.from_error(err)
