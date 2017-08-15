from django import template

register = template.Library()

@register.filter
def get_it(value, arg):
	return value[arg]