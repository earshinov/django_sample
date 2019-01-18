from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import expressions, fields
from django.utils.timezone import datetime
import pytz
from rest_framework.test import APITestCase

import ddl

from .models import Order, Product


CHICKEN_PRICE = 5
RICE_PRICE = 1
PASTA_PRICE = 2
TOTAL_ORDERS = 3


USER_JDOE = {
    'username': 'jdoe',
    'first_name': 'Jane',
    'last_name': 'Doe',
    'email': 'jdoe@example.com',
}
USER_JSMITH = {
    'username': 'jsmith',
    'first_name': 'John',
    'last_name': 'Smith',
    'email': 'jsmith@example.com',
}
USER_JWERNER = {
    'username': 'jwerner',
    'first_name': 'John',
    'last_name': 'Werner',
    'email': 'jwerner@example.com',
}

ORDER1 = {
    'id': 1,
    'created_date': '2017-01-01T00:00:00Z',
    'submitted_date': '2017-01-02T00:00:00Z',
    'submitted': True,
    'user': USER_JDOE,
    'total_products': 3,
}
ORDER2 = {
    'id': 2,
    'created_date': '2019-01-01T00:00:00Z',
    'submitted_date': None,
    'submitted': False,
    'user': USER_JSMITH,
    'total_products': 2,
}
ORDER3 = {
    'id': 3,
    'created_date': '2018-01-01T00:00:00Z',
    'submitted_date': '2018-01-02T00:00:00Z',
    'submitted': True,
    'user': USER_JWERNER,
    'total_products': 2,
}

ORDER1_WITHOUT_ANNOTATED_FIELDS = {
    'id': 1,
    'created_date': '2017-01-01T00:00:00Z',
    'submitted_date': '2017-01-02T00:00:00Z',
    'user': USER_JDOE,
}
ORDER2_WITHOUT_ANNOTATED_FIELDS = {
    'id': 2,
    'created_date': '2019-01-01T00:00:00Z',
    'submitted_date': None,
    'user': USER_JSMITH,
}
ORDER3_WITHOUT_ANNOTATED_FIELDS = {
    'id': 3,
    'created_date': '2018-01-01T00:00:00Z',
    'submitted_date': '2018-01-02T00:00:00Z',
    'user': USER_JWERNER,
}


class BaseTestCase(APITestCase):

    def setUp(self):
        self.add_fixtures()

    @classmethod
    def add_fixtures(cls):
        jsmith = User.objects.create_user(username='jsmith', email='jsmith@example.com', first_name='John', last_name='Smith')
        jdoe = User.objects.create_user(username='jdoe', email='jdoe@example.com', first_name='Jane', last_name='Doe')
        jwerner = User.objects.create_user(username='jwerner', email='jwerner@example.com', first_name='John', last_name='Werner')

        test_group = Group.objects.create(name='test')
        test_group.user_set.add(jdoe)
        test_group.user_set.add(jwerner)

        chicken = Product.objects.create(name='Chicken', price=CHICKEN_PRICE)
        rice = Product.objects.create(name='Rice', price=RICE_PRICE)
        pasta = Product.objects.create(name='Pasta', price=PASTA_PRICE)

        order1 = Order.objects.create(user=jdoe, submitted_date=datetime(2017, 1, 2, 0, 0, 0, tzinfo=pytz.UTC))
        order1.created_date = datetime(2017, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        order1.save()
        order1.order_lines.create(product=chicken, quantity=1, total_price=1 * CHICKEN_PRICE)
        order1.order_lines.create(product=rice, quantity=2, total_price=2 * RICE_PRICE)

        order2 = Order.objects.create(user=jsmith)
        order2.created_date = datetime(2019, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        order2.save()
        order2.order_lines.create(product=chicken, quantity=2, total_price=2 * CHICKEN_PRICE)

        order3 = Order.objects.create(user=jwerner, submitted_date=datetime(2018, 1, 2, 0, 0, 0, tzinfo=pytz.UTC))
        order3.created_date = datetime(2018, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        order3.save()
        order3.order_lines.create(product=chicken, quantity=1, total_price=1 * CHICKEN_PRICE)
        order3.order_lines.create(product=pasta, quantity=1, total_price=1 * PASTA_PRICE)



class TestOrderingFilter(BaseTestCase):
    """
    Test various kinds of OrderingFilter field definitions
    """

    order1: Order
    order2: Order
    order3: Order

    def setUp(self):
        super().setUp()
        [self.order1, self.order2, self.order3] = Order.objects.all().order_by('id')

    def test_field_name(self):
        self._test_ordering('id', ddl.OrderingFilter(fields={'id': 'id'}), self.order1)

    def test_field_names_list(self):
        self._test_ordering('user', ddl.OrderingFilter(fields={'user': ('user__first_name', 'user__last_name')}), self.order1)

    def test_expr(self):
        expr = expressions.ExpressionWrapper(models.Q(submitted_date__isnull=False), output_field=fields.BooleanField())
        self._test_ordering('submitted', ddl.OrderingFilter(fields={'submitted': expr}), self.order2)

    def test_expr_list(self):
        self._test_ordering('user', ddl.OrderingFilter(fields={'user': (models.F('user__first_name'), models.F('user__last_name'))}), self.order1)

    def test_obj(self):
        self._test_ordering('id', ddl.OrderingFilter(fields={'id': {'expr': models.F('id')}}), self.order1)

    def test_obj_list(self):
        self._test_ordering('user', ddl.OrderingFilter(fields={'user': {'exprs': (models.F('user__first_name'), models.F('user__last_name'))}}), self.order1)

    def test_obj_with_field_name(self):
        self._test_ordering('id', ddl.OrderingFilter(fields={'id': {'expr': 'id'}}), self.order1)

    def test_obj_list_with_field_names(self):
        self._test_ordering('user', ddl.OrderingFilter(fields={'user': {'exprs': ('user__first_name', 'user__last_name')}}), self.order1)

    def test_invalid_obj(self):
        with self.assertRaisesMessage(ValueError, "Expected 'exprs' or 'expr'"):
            ddl.OrderingFilter(fields={'id': {}})

    def test_ordering_by_unknown_field(self):
        self._test_ordering('unknown,id', ddl.OrderingFilter(fields={'id': 'id'}), self.order1)

    def test_ordering_desc(self):
        self._test_ordering('-id', ddl.OrderingFilter(fields={'id': 'id'}), self.order3)

    def _test_ordering(self, ordering, filter: ddl.OrderingFilter, expected_first_order: Order):
        actual_order = filter.filter(Order.objects.all(), [ordering]).first()
        self.assertEqual(expected_first_order, actual_order)
