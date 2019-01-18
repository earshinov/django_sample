import unittest

from django.db.models.signals import pre_save

from lib.temp_disconnect_signal import temp_disconnect_signal
from . import models


INVALID_CHOICE = 'unknown'


class ChoicesFieldTestCase(unittest.TestCase):

    def test_choices_validation(self):
        """
        Test that `choices` are validated only in `full_clean`.

        Choices are not validated during `save`, and `clean()` is also not enough.
        Related:
          - https://code.djangoproject.com/ticket/29549
          - https://stackoverflow.com/a/32431937/675333
        """
        with temp_disconnect_signal(signal=pre_save, receiver=models.pre_save_handler):

            test1 = models.Test(choices_field=INVALID_CHOICE)
            # does not raise
            test1.save()

            test2 = models.Test(choices_field=INVALID_CHOICE)
            # does not raise
            test2.clean()
            test2.save()

            test3 = models.Test(choices_field=INVALID_CHOICE)
            self.assertRaises(Exception, lambda: test3.full_clean())
            test3.save()
