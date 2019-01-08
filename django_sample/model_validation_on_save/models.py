from enum import Enum

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


class ChoiceEnum(Enum):
    """
    Used to enable enums in django.
    Define your custom enum by deriving from this class:
        class StutterEnum(ChoiceEnum):
        NONE = 'None'
        GOOD = 'Good'
        FAIR = 'Fair'
        BAD = 'Bad'

    Use it in Django model:
    dx12_stutter_nv = models.CharField(max_length=4, choices=StutterEnum.choices(), default=StutterEnum.NONE)
    """

    @classmethod
    def choices(cls):
        return tuple((x.name, x.value) for x in cls)


class CHOICES(ChoiceEnum):
    one = 'One'
    two = 'Two'


class Test(models.Model):
    choices_field = models.CharField(max_length=10, choices=CHOICES.choices())


# Validate model instances on save.
# https://code.djangoproject.com/ticket/29549
# https://stackoverflow.com/questions/4441539/why-doesnt-djangos-model-save-call-full-clean
@receiver(pre_save)
def pre_save_handler(sender, instance, *args, **kwargs):
    instance.full_clean()
