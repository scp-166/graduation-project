from django.core.management.base import BaseCommand
from os import sep, curdir

from apps.exhibition.models import TerminalCategory, TerminalInfo


# 后面写初始化表
class Command(BaseCommand):
    """
    python manage.py initgroup 可以启动
    创建分组
    """
    def handle(self, *args, **options):
        # import sys
        # print(sys.argv[0])  # manage.py 因为运行就是python manage.py initTable
        # ./conf/category.conf
        with open(curdir+sep+'conf'+sep+'category.conf') as f:
            conf = eval(f.read())
        for category_id, category_name in conf.items():
            if not TerminalCategory.objects.filter(category_id=category_id).exists():
                terminal_category = TerminalCategory.objects.create(category_id=category_id, category_name=category_name)

                print("{} 创建成功".format(terminal_category))
                print(category_id, category_name)
            else:
                print("{} 已经存在".format(TerminalCategory.objects.filter(category_id=category_id).first()))


