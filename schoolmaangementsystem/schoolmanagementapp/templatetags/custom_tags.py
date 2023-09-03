from django import template

register = template.Library()

@register.filter(name='split')
def split(value, key):
  """
    Returns the value turned into a list.
  """
  return value.split(key)



@register.filter(name='split_email')
def split_email(value):
    """Split the email at '@' and retrieve the username part."""
    return value.split('@')[0] if '@' in value else value