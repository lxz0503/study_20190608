from django.db import models

# Create your models here.


class Product(models.Model):
    product_name = models.CharField('product name', max_length=64)
    product_desc = models.CharField('product desc', max_length=200)
    product_owner = models.CharField('product owner', max_length=200)
    create_time = models.DateTimeField('create time', auto_now=True)

    class Meta:
        verbose_name = 'product management'
        verbose_name_plural = 'product_management'

    def __str__(self):
        return self.product_name
