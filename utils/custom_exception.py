"""
自定义异常
"""


class CustomError(Exception):
    """
    自定义异常
    """
    def __init__(self, desc, custom_desc='', separator=''):
        """
        自定义异常处理
        :param desc: 总描述
        :param custom_desc:  详细描述
        """
        super(CustomError, self).__init__()
        self._error_desc = desc + custom_desc
        self._separator = separator

    def __str__(self):
        return self._separator+self._error_desc+self._separator


class SerialProcessError(CustomError):
    """
    串口处理函数异常
    """
    def __init__(self, desc="串口处理函数异常:\n", custom_desc='', separator="\n"+'*'*10+"\n"):
        super(SerialProcessError, self).__init__(desc, custom_desc, separator)


class DataProcessError(CustomError):
    """
    数据处理函数异常
    """
    def __init__(self, desc="数据处理函数出现异常:\n", custom_desc='', separator='\n'+'-'*10+'\n'):
        super(DataProcessError, self).__init__(desc, custom_desc, separator)


class NetWorkProcessError(CustomError):
    """
    网络通信函数异常
    """
    def __init__(self, desc="网络通信函数出现异常:", custom_desc='', separator='\n'+'#'*10+'\n'):
        super(NetWorkProcessError, self).__init__(desc, custom_desc, separator)


class CommandProcessError(CustomError):
    """
    指令处理函数异常
    """
    def __init__(self, desc="指令处理函数异常:", custom_desc='', separator='\n'+'&'*10+'\n'):
        super(CommandProcessError, self).__init__(desc, custom_desc, separator)


class SessionLoginError(CustomError):
    """
    session login登陆异常
    """
    def __init__(self, desc="指令处理函数异常:"):
        super(SessionLoginError, self).__init__(desc)


if __name__ == '__main__':
    pass

