import typing

from django.db import models
from django.db.models import expressions
from django.forms.utils import pretty_name
from django.utils.translation import ugettext_lazy as _

from django_filters import filters
from django_filters.constants import EMPTY_VALUES

__all__ = ('OrderingFilter',)


class OrderingFilter(filters.BaseCSVFilter, filters.ChoiceFilter):
    """
    An alternative to django_filters.filter.OrderingFilter that allows to specify any Django ORM "expression" for ordering.

    Usage examples:

      class MyOrderingFilter(ddf.OrderingFilter):
        def __init__(self):
          super().__init__(fields={

            # a model field
            'id': 'id'

            # an expression
            'published_by':
              functions.Concat(
                expressions.F(f'published_user__first_name'),
                expressions.Value(' '),
                expressions.F(f'published_user__last_name')
              ),

            # a complete field descriptor with custom field label
            'reported_by': {
              'label': 'Reporter',
              'desc_label': 'Reporter (descending)',  # optional, would be derived from 'label' anyway
              'expr': functions.Concat(
                expressions.F(f'reported_user__first_name'),
                expressions.Value(' '),
                expressions.F(f'reported_user__last_name')
              ),
            }
          })

    For more information about expressions, please see the official Django documentation at
    https://docs.djangoproject.com/en/2.1/ref/models/expressions/
    """

    _fields: typing.Mapping[str, 'FieldDescriptor']

    def __init__(self, fields: typing.Mapping[str, typing.Any]):
        self._fields = normalize_fields(fields)
        super().__init__(choices=build_choices(self._fields))

    # @override
    def filter(self, qs: models.QuerySet, value: typing.Union[typing.List[str], None]):
        return qs if value in EMPTY_VALUES else qs.order_by(*(expr for expr in map(self.get_ordering_expr, value)))

    def get_ordering_expr(self, param) -> expressions.Expression:
        descending = param.startswith('-')
        param = param[1:] if descending else param
        field_descriptor = self._fields.get(param)
        return None if field_descriptor is None else \
            field_descriptor.expr if not descending else field_descriptor.expr.desc()


def normalize_fields(fields: typing.Mapping[str, typing.Any]) -> typing.Mapping[str, 'FieldDescriptor']:
    return dict((
        param_name,
        FieldDescriptor(param_name, {'expr': normalize_expr(field)} if isinstance(field, (str, expressions.Expression)) else field)
    ) for param_name, field in fields.items())


def normalize_expr(expr: typing.Union[str, expressions.Expression]):
    return models.F(expr) if isinstance(expr, str) else expr


descending_fmt = _('%s (descending)')


class FieldDescriptor:
    expr: models.Expression

    def __init__(self, param_name: str, data: typing.Mapping[str, typing.Any]):
        self.expr = normalize_expr(data['expr'])
        self.label = data.get('label', _(pretty_name(param_name)))
        self.desc_label = data.get('desc_label', descending_fmt.format(self.label))


def build_choices(fields: typing.Mapping[str, 'FieldDescriptor']):
    choices = []
    for param_name, field_descriptor in fields.items():
        choices.append((param_name, field_descriptor.label))
        choices.append((f'-{param_name}', field_descriptor.desc_label))
    return choices
