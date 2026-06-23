from django.db import models

from pytils.translit import slugify


class Product(models.Model):
    name = models.CharField('Название товара', max_length=255)
    sku = models.CharField('Артикул', max_length=50, unique=True)
    slug = models.SlugField('URL', max_length=255, unique=True, blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    stock = models.IntegerField('Остаток на складе', default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if Product.objects.filter(slug=base_slug).exists():
                self.slug = f"{base_slug}-{self.sku}"
            else:
                self.slug = base_slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.sku}] {self.name}"
