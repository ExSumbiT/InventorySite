from django.db import models
from django.contrib.auth.models import User


class QrParameters(models.Model):
    user = models.OneToOneField(User, related_name='qr', on_delete=models.CASCADE, primary_key=True)
    weight = models.IntegerField(default=30)
    height = models.IntegerField(default=50)
    font = models.CharField(default='arial', max_length=40)
    font_size = models.IntegerField(default=14)
    description_logo = models.BooleanField(default=True)
    logo_size = models.IntegerField(default=30)

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            try:
                self.user = User.objects.get(id=user)
            except:
                self.user = User.objects.get(id=user.id)
    
    def update(self, *args, **kwargs):
            for name, values in kwargs.items():
                try:
                    print(name, values)
                    setattr(self,name,values)
                except KeyError:
                    pass
            self.save()
    
    def items(self):
        return {k: v for k, v in self.__dict__}