from django.db import models
from product.models import Product

# Create your models here.

class Bug(models.Model):
    Product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=True)  # 关联产品ID
    bug_name = models.CharField('bug name', max_length=64)
    bug_detail = models.CharField('bug detail', max_length=200)
    status_tuple = (('opened','opened'), ('resolved','resolved'), ('fixed','fixed'), ('closed','closed'))
    bug_status = models.CharField(verbose_name='status', choices=status_tuple, default='opened', max_length=64,null=True)
    level_tuple = (('1','1'), ('2','2'), ('3','3'))
    bug_level = models.CharField(verbose_name='severity', choices=level_tuple,default='3',max_length=8,null=True)
    bug_creator = models.CharField('creator',max_length=64)
    bug_assignee = models.CharField('assignee', max_length=64)
    created_time = models.DateTimeField('created time', auto_now=True)

    class Meta:
        verbose_name = 'bug management'
        verbose_name_plural = 'bug management'

    def __str__(self):
        return self.bug_name


