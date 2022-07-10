from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.dispatch import receiver


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

    def __init__(self, *args, **kwargs):
        super(InventoryType, self).__init__(*args, **kwargs)
        self.initial_parameters = set(self.parameters.all())


@receiver(m2m_changed, sender=InventoryType.parameters.through)
def my_sign(sender, instance, *args, **kwargs):
    action = kwargs.pop('action', None)
    old = set(instance.parameters.all())
    new = instance.initial_parameters
    if action == 'post_add':
        parameters = old - new
        for inv in Inventory.objects.filter(type=instance).all():
            for parameter in parameters:
                if not Inventory.objects.filter(type=instance, parameter=parameter, index=inv.index).count() > 0:
                    Inventory.objects.create(parameter=parameter, type=instance, index=inv.index)
    if action == 'post_remove':
        parameters = new - old
        for parameter in parameters:
            for inv in Inventory.objects.filter(type=instance, parameter=parameter).all():
                if Inventory.objects.filter(type=instance, parameter=parameter, index=inv.index).count() > 0:
                    inv.delete()


class Inventory(models.Model):
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, blank=True, null=True)
    type = models.ForeignKey(InventoryType, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(blank=True, auto_now_add=True)
    value = models.CharField(max_length=100, blank=True, default='')
    index = models.IntegerField(null=False)

    class Meta:
        unique_together = (("type", "parameter", "index"),)

    def __str__(self):
        return f'{self.index}. {self.type.full_name}-{self.parameter.name}'
