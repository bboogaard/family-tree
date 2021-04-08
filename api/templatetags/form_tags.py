from django import template


register = template.Library()


@register.inclusion_tag('templatetags/field_errors.html')
def render_field_errors(error_list):
    return {
        'errors': [str(error) for error in error_list]
    }
