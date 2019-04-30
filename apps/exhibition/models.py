from django.db import models


class TerminalCategory(models.Model):
    category_id = models.PositiveSmallIntegerField(primary_key=True, verbose_name="设备种类id")
    category_name = models.CharField(max_length=20, verbose_name="设备种类名称")

    def __str__(self):
        return "终端种类: <{}>".format(self.category_name)

    class Meta:
        verbose_name = verbose_name_plural = "终端设备种类"


class TerminalInfo(models.Model):
    terminal_category = models.ForeignKey(TerminalCategory, on_delete=models.CASCADE, verbose_name="设备种类id")
    terminal_id = models.PositiveSmallIntegerField(verbose_name="终端id")
    terminal_name = models.CharField(max_length=20, verbose_name="终端名称")
    status = models.BooleanField(default=False,  verbose_name="终端状态")

    def __str__(self):
        return "终端信息:{}".format(self.terminal_name)

    class Meta:
        unique_together = (('terminal_category', 'terminal_id'), )
        verbose_name = verbose_name_plural = "终端信息"


class TerminalData(models.Model):
    terminal = models.ForeignKey(TerminalInfo, on_delete=models.CASCADE, verbose_name="终端id")
    data = models.FloatField(default=0.0, verbose_name="终端数据")
    create_time = models.DateField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return "终端: <{}>".format(self.terminal_id)

    class Meta:
        verbose_name = verbose_name_plural = "终端数据"

