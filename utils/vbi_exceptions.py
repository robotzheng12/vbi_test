"""
VBI core exceptions

These exceptions are documented in docs/topics/exceptions.rst. Please don't add
new exceptions here without documenting them there.
"""


class NetworkError(Exception):
    """
    登录失败
    """

    def __init__(self, message):
        self.message = message


class LoginError(Exception):
    """
    登录失败
    """

    def __init__(self, message):
        self.message = message


class ImageLoadError(Exception):
    """
    图像加载失败
    """
    pass


class ImageNotExist(Exception):
    """
    图像不存在
    """
    pass


class ImageLoadTimeout(Exception):
    """
    图像加载超时
    """
    pass
