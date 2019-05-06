from django import template

register = template.Library()


@register.filter
def add_str(arg1, arg2):
    """concatenate arg1 & arg2

    Using in template:
    '{{ arg1|add_str:arg2 }}'
    """
    return str(arg1) + str(arg2)


@register.simple_tag
def call_method(obj, method_name, *args):
    """Call method_name from obj with *args.

    Using in template:
    {% call_method obj 'get_something' '10' %}
    """
    method = getattr(obj, method_name)
    return method(*args)


@register.filter
def name(obj):
    """return the object name

    Using in template:
    '{{ obj|name }}'
    """
    return obj.__class__.__name__
