from django import template

register = template.Library()

@register.simple_tag
def get_rating_value(ratings_dict, restaurant_id, field):
    try:
        return ratings_dict.get(restaurant_id, {}).get(field, "Not yet rated")
    except Exception:
        return "Not yet rated"