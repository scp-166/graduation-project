from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(self, telephone, password, username, **kwargs):
        if not telephone:
            raise ValueError("请输入手机号码")
        if not password:
            raise ValueError("请输入密码")
        if not username:
            raise ValueError("请输入用户名")

        user = self.model(telephone=telephone, username=username, **kwargs)
        user.set_password(password)
        user.save()  # 记得调用save!
        return user

    def create_user(self, telephone, password, username, **kwargs):
        kwargs["is_superuser"] = False
        kwargs["is_staff"] = False
        return self._create_user(telephone, password, username, **kwargs)

    def create_superuser(self, telephone, password, username, **kwargs):
        kwargs["is_superuser"] = True
        kwargs["is_staff"] = True
        return self._create_user(telephone, password, username, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    telephone = models.CharField(max_length=11, unique=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True)  # 没有null=True,则存储的时候会存储为空字符串，则为变成唯一
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'telephone'    # 验证时username代表的字段是telephone
    REQUIRED_FIELDS = ['username']  # 创建超级用户的时候，需要键入值的字段，默认还包括USERNAME_FIELD定义的字段和password
    EMAIL_FIELD = 'email'

    objects = UserManager()  # 注意写法

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
