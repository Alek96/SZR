from django.template import Context, Template
from django.test import SimpleTestCase


class AddStrTest(SimpleTestCase):
    def test_rendered(self):
        str = 'string'
        context = Context({'str': str})
        template_to_render = Template(
            '{% load core_extras %}'
            '{{ str|add_str:"-"|add_str:str }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('{}-{}'.format(str, str), rendered_template)
        self.assertEqual(rendered_template, '{}-{}'.format(str, str))


class CallMethodTest(SimpleTestCase):
    def test_rendered(self):
        class Adder:
            count = 0

            def add_number(self, number):
                self.count += number
                return self.count

        adder = Adder()
        context = Context({'adder': adder})
        template_to_render = Template(
            '{% load core_extras %}'
            '{% call_method adder "add_number" 10 %}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('10', rendered_template)
        self.assertEqual(rendered_template, '10')


class NameTest(SimpleTestCase):
    def test_rendered(self):
        obj = {}
        context = Context({'obj': obj})
        template_to_render = Template(
            '{% load core_extras %}'
            '{{ obj|name }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('{}'.format(dict.__name__), rendered_template)
        self.assertEqual(rendered_template, '{}'.format(dict.__name__))
