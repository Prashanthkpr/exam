from django import template

register = template.Library()

@register.filter
def split_string(value):
	file_extension=value.split('.')[-1]
	return file_extension
