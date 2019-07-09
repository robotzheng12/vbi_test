"""
VBI core exceptions

These exceptions are documented in docs/topics/exceptions.rst. Please don't add
new exceptions here without documenting them there.
"""


class LoginError(Exception):
    """
    登录失败
    """
    def __init__(self,*arg):
        pass


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
