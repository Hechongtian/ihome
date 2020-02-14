from django.db import models


class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True,
                                       verbose_name="更新时间")

    class Meta:
        # 抽象类只用来被继承，不会被迁移进数据库
        abstract = True
