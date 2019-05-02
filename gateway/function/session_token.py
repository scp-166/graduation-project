import json
import requests
import re
import sys

sys.path.append('../..')

from utils.cache_process import cookie_cache_processor
from utils.custom_exception import SessionLoginError


class AuthProcessor:
    def __init__(self):
        """
        授权相关的processor
        """
        self._login_url = 'http://127.0.0.1:8000/auth/token_login/'
        self._token_url = 'http://127.0.0.1:8000/auth/token/'
        self._telephone = None
        self._password = None
        self._session = requests.Session()  # 保持唯一窗口
        self._appropriate_headers = {  # 请求头
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        self._csrf_token = None
        self._form_data = None

    def login(self):
        if self.telephone is None or self.password is None:
            raise SessionLoginError("手机号或密码为空")
        else:
            self._csrf_token = self._get_csrf_token()
            self._login()

    def get_token(self):
        if self.telephone is None or self.password is None:
            raise SessionLoginError("手机号或密码为空")
        else:
            # 获取csrf_token
            self._csrf_token = self._get_csrf_token()
            self._get_token()

    def _get_csrf_token(self):
        """
        通过session的一致性获得csrf_token
        :return:
        """
        ret = self._session.get(self.login_url, headers=self._appropriate_headers)  # 获得页面 bytes
        reg = r"<input type='hidden' name='csrfmiddlewaretoken' value='(.*)'>"  # 为了拿到 csrftoken
        pattern = re.compile(reg)
        result = pattern.findall(ret.content.decode())  # 从注册页中正则匹配，获取 csrftoken
        if result:
            csrf_token = result[0]  # 拿到匹配项的第一个，其实只有一个
            return csrf_token
        else:
            self._session.close()
            raise SessionLoginError("token未拿到")

    def _get_token(self):
        self._set_form_data()

        ret = self._session.post(self.token_url, headers=self._appropriate_headers, data=self._form_data)  # 期望是JsonResponse
        # 获得自定义的状态码
        if 'code' in ret.text:
            if json.loads(ret.text)['code'] == 200:  # 登陆成功
                # 保存cookies
                cookies = requests.utils.dict_from_cookiejar(self._session.cookies)  # dict-like
                cookie_cache_processor.set_verification(cookies['token'][1:-1])  # 保存进缓存, 注意token是存在引号，需要去除
                # 保存进文件
                with open("cookies.txt", "w+") as fp:
                    json.dump(cookies, fp)
            else:
                raise SessionLoginError("登陆失败")
        else:
            raise SessionLoginError("无结果，登陆失败")

    def _login(self):
        self._set_form_data()
        print(self._form_data)

        ret = self._session.post(self.login_url, headers=self._appropriate_headers,
                                 data=self._form_data)  # 期望是JsonResponse
        # 获得自定义的状态码
        print(ret.text)
        if 'code' in ret.text:
            if json.loads(ret.text)['code'] == 200:  # 登陆成功
                # 保存cookies
                cookies = requests.utils.dict_from_cookiejar(self._session.cookies)  # dict-like
                cookie_cache_processor.set_verification(cookies['token'][1:-1])  # 保存进缓存, 注意token是存在引号，需要去除
                # 保存进文件
                with open("session_id.txt", "w+") as fp:
                    json.dump(cookies, fp)
            else:
                raise SessionLoginError("登陆失败")
        else:
            raise SessionLoginError("无结果，登陆失败")

    def _set_form_data(self):
        """
        一开始_form_data为None
        用到需要重新更新下数据
        :return:
        """
        self._form_data = {
            'csrfmiddlewaretoken': self._csrf_token,
            'telephone': self.telephone,
            'password': self.password
        }

    def close(self):
        """
        关闭session窗口
        :return:
        """
        self._session.close()

    @property
    def telephone(self):
        return self._telephone

    @telephone.setter
    def telephone(self, value):
        self._telephone = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def login_url(self):
        return self._login_url

    @login_url.setter
    def login_url(self, value):
        self._login_url = value

    @property
    def token_url(self):
        return self._token_url

    @token_url.setter
    def token_url(self, value):
        self._token_url = value


auth_processor = AuthProcessor()


if __name__ == '__main__':
    auth_processor.telephone = 17875512067
    auth_processor.password = 'abc666666'
    # auth_processor.login()
    auth_processor.get_token()
