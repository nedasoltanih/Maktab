from django import template

register = template.Library()

@register.tag(name='cut')
def cut(value, arg):
    return value.replace(arg, "")

@register.simple_tag
def num_tasks(value):
    return len(value)