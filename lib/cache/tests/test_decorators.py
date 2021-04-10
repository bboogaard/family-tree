from django.contrib.auth.models import User
from django.core.cache import cache
from django.test.testcases import SimpleTestCase

from lib.cache.decorators import cache_method_result, cache_result


@cache_result('test-result')
def test_func(arg1, arg2):
    return arg1 + arg2


class TestClass:

    foo = 'bar'

    @cache_method_result('test-method-result')
    def test_func(self, arg1, arg2):
        return arg1 + arg2

    @cache_method_result('test-object-result')
    def test_func_with_model_instance(self, arg1):
        return str(arg1)

    @cache_method_result('test-list-result')
    def test_func_with_list(self, arg1):
        return ','.join(arg1)

    @cache_method_result('test-method-result-attrs', key_attrs=['foo'])
    def test_func_with_attrs(self, arg1, arg2):
        return arg1 + arg2


class TestDecorators(SimpleTestCase):

    def test_cache_result(self):
        result = test_func(1, 1)
        expected = 2
        self.assertEqual(result, expected)

        result = cache.get_entry('test-result:1:1')
        expected = 2
        self.assertEqual(result, expected)

    def test_cache_method_result(self):
        obj = TestClass()
        result = obj.test_func(1, 1)
        expected = 2
        self.assertEqual(result, expected)

        result = cache.get_entry('test-method-result:1:1')
        expected = 2
        self.assertEqual(result, expected)

    def test_cache_method_result_with_attr(self):
        obj = TestClass()
        result = obj.test_func_with_attrs(1, 1)
        expected = 2
        self.assertEqual(result, expected)

        result = cache.get_entry('test-method-result-attrs:foo=bar:1:1')
        expected = 2
        self.assertEqual(result, expected)

    def test_cache_with_model_instance(self):
        user = User(pk=1, username='johndoe')
        obj = TestClass()
        result = obj.test_func_with_model_instance(user)
        expected = 'johndoe'
        self.assertEqual(result, expected)

        result = cache.get_entry('test-object-result:1')
        expected = 'johndoe'
        self.assertEqual(result, expected)

    def test_cache_with_list(self):
        obj = TestClass()
        result = obj.test_func_with_list(['foo', 'bar'])
        expected = 'foo,bar'
        self.assertEqual(result, expected)

        result = cache.get_entry('test-list-result:foo:bar')
        expected = 'foo,bar'
        self.assertEqual(result, expected)

    def test_cache_with_kwarg(self):
        result = test_func(1, arg2=1)
        expected = 2
        self.assertEqual(result, expected)

        result = cache.get_entry('test-result:1:arg2=1')
        expected = 2
        self.assertEqual(result, expected)
