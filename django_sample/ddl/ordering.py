import collections
import itertools
import typing

from django.db import models
from django.db.models import expressions
from django.forms.utils import pretty_name
from django.utils.translation import ugettext_lazy as _

from django_filters import filters
from django_filters.constants import EMPTY_VALUES

__all__ = ('OrderingFilter',)


class OrderingFilter(filters.BaseCSVFilter, filters.ChoiceFilter):
    """An alternative to :class:`django_filters.filters.OrderingFilter` that allows to specify any Django ORM expression for ordering.

    Usage example:

    .. code-block:: python

      from django.db import models
      from django.db.models import aggregates, expressions, fields

      import ddl

      class OrderOrderingFilter(ddl.OrderingFilter):
        def __init__(self):
          super().__init__(fields={

            # a model field
            'created': 'created'

            # an expression
            'submitted': expressions.ExpressionWrapper(
                models.Q(submitted_date__isnull=False),
                output_field=fields.BooleanField()
            ),

            # multiple fields or expressions
            'user': ('user__first_name', 'user__last_name'),

            # a complete field descriptor with custom field label
            'products': {
              'label': 'Total number of items in the order',
              # if not specified, `desc_label` would be derived from 'label' anyway
              'desc_label': 'Total number of items in the order (descending)',
              'expr': aggregates.Sum('order_lines__quantity'),
              # it is also possible to filter by multiple fields or expressions here
              #'exprs': (...)
            },
          })

    For more information about expressions, see the official Django documentation at
    https://docs.djangoproject.com/en/dev/ref/models/expressions/
    """

    _fields: typing.Mapping[str, 'FieldDescriptor']

    def __init__(self, fields: typing.Mapping[str, typing.Any]):
        self._fields = normalize_fields(fields)
        super().__init__(choices=build_choices(self._fields))

    # @override
    def filter(self, qs: models.QuerySet, value: typing.Union[typing.List[str], None]):
        return qs if value in EMPTY_VALUES else qs.order_by(*(itertools.chain(*(self.__get_ordering_exprs(param) for param in value))))

    def __get_ordering_exprs(self, param) -> typing.Union[None, typing.List[expressions.Expression]]:
        descending = param.startswith('-')
        param = param[1:] if descending else param
        field_descriptor = self._fields.get(param)
        return () if field_descriptor is None else \
            field_descriptor.exprs if not descending else \
            (expr.desc() for expr in field_descriptor.exprs)


def normalize_fields(fields: typing.Mapping[str, typing.Any]) -> typing.Mapping[str, 'FieldDescriptor']:
    return dict((
        param_name,
        FieldDescriptor(param_name, field if isinstance(field, collections.Mapping) else {'exprs': normalize_exprs(field)})
    ) for param_name, field in fields.items())

def normalize_exprs(exprs: typing.Union[
        typing.Union[str, expressions.Expression],
        typing.List[typing.Union[str, expressions.Expression]]
    ]) -> typing.List[expressions.Expression]:
    # `exprs` is either a single expression or a Sequence of expressions
    exprs = exprs if isinstance(exprs, collections.Sequence) and not isinstance(exprs, str) else (exprs,)
    return [normalize_expr(expr) for expr in exprs]

def normalize_expr(expr: typing.Union[str, expressions.Expression]) -> expressions.Expression:
    return models.F(expr) if isinstance(expr, str) else expr


descending_fmt = _('%s (descending)')


class FieldDescriptor:
    exprs: typing.List[models.Expression]

    def __init__(self, param_name: str, data: typing.Mapping[str, typing.Any]):
        exprs = data.get('exprs') or data.get('expr')
        if not exprs:
            raise ValueError("Expected 'exprs' or 'expr'")
        self.exprs = normalize_exprs(exprs)
        self.label = data.get('label', _(pretty_name(param_name)))
        self.desc_label = data.get('desc_label', descending_fmt.format(self.label))


def build_choices(fields: typing.Mapping[str, 'FieldDescriptor']):
    choices = []
    for param_name, field_descriptor in fields.items():
        choices.append((param_name, field_descriptor.label))
        choices.append((f'-{param_name}', field_descriptor.desc_label))
    return choices
