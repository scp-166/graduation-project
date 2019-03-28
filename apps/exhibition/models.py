from django.db import models


class TerminalType(models.Model):
    type_id = models.AutoField(primary_key=True, verbose_name="设备种类id")
    type_name = models.CharField(max_length=20, verbose_name="设备种类名称")

    def __str__(self):
        return "终端种类: <{}>".format(self.type_name)

    class Meta:
        verbose_name = verbose_name_plural = "终端设备种类"


class TerminalInfo(models.Model):
    type_id = models.ForeignKey(TerminalType, on_delete=models.CASCADE, verbose_name="设备种类id")
    terminal_id = models.SmallIntegerField(verbose_name="终端id")
    terminal_name = models.CharField(max_length=20, verbose_name="终端名称")

    def __str__(self):
        return "终端信息:{}".format(self.terminal_name)

    class Meta:
        verbose_name = verbose_name_plural = "终端信息"


class TerminalData(models.Model):
    terminal_id = models.ForeignKey(TerminalInfo, on_delete=models.CASCADE, verbose_name="终端id")

    data = models.FloatField(default=0.0, verbose_name="终端数据")
    status = models.BooleanField(default=False,  verbose_name="终端状态")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return "终端: <{}>".format(self.terminal_id)

    class Meta:
        verbose_name = verbose_name_plural = "终端数据"
