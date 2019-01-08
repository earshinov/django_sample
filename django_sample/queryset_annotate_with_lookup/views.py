import logging

from django.db import models
from django.db.models import expressions
from rest_framework import fields, serializers, viewsets

from .models import TestModel

logger = logging.getLogger()


class TestModelSerializer(serializers.ModelSerializer):
    has_user = fields.BooleanField()

    class Meta:
        model = TestModel
        fields = ('id', 'has_user')


class TestViewSet(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer

    class Meta:
        model = TestModel

    def get_queryset(self) -> models.QuerySet:
        qs = self.queryset.annotate(has_user=
            expressions.Case(
                expressions.When(
                    user__isnull=False,
                    then=expressions.Value(True),
                ),
                default=expressions.Value(False),
                #
                # Tell Django the expected type of the field, see `output_field` in
                # https://docs.djangoproject.com/en/2.1/ref/models/expressions/
                #
                output_field=models.BooleanField()
            )
        )
        logger.info(qs.query)
        return qs
