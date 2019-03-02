from django.test import SimpleTestCase
from django.template import Context, Template


class AddStrTemplateTagTest(SimpleTestCase):
    def test_rendered(self):
        str = 'string'
        context = Context({'str': str})
        templte_to_render = Template(
            '{% load core_extras %}'
            '{{ str|add_str:"-"|add_str:str }}'
        )
        rendered_template = templte_to_render.render(context)
        self.assertInHTML(str + '-' + str, rendered_template)
