from django.db import models


class Parameter(models.Model):
    name = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    html_type = models.CharField(max_length=20)
    order = models.IntegerField(default=1)
    show = models.BooleanField(default=True)
    date = models.DateTimeField(blank=True, auto_now_add=True)

    class Meta:
        ordering = ['order', ]

    def __str__(self):
        return f'{self.order}. {self.name}'


class InventoryType(models.Model):
    full_name = models.CharField(max_length=20)
    short_name = models.CharField(max_length=5)
    parameters = models.ManyToManyField(Parameter, related_name='parameters')

    def __unicode__(self):
        return self.full_name

    def __str__(self):
        return self.full_name


class Inventory(models.Model):
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, blank=True, null=True)
    type = models.ForeignKey(InventoryType, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(blank=True, auto_now_add=True)
    value = models.CharField(max_length=100, blank=True)
    index = models.IntegerField(null=True)

    class Meta:
        unique_together = (("type", "parameter", "index"),)

    def __str__(self):
        return f'{self.index}. {self.type.full_name}-{self.parameter.name}'
