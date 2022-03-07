from django import template

from workspace.models import SchedulePost

register = template.Library()


def schedule_day_filter(day, start_index=0):
    print(day, start_index)
    results = SchedulePost.objects.filter(day__name__iexact = day)
    # results = schedule_query_set.filter(day__name__iexact = day)
    return results[int(start_index):]

def index_at(query_set, index):
    try:
        return query_set[int(index)]
    except:
        return None

register.filter('schedule_day_filter', schedule_day_filter)
register.filter('index_at', index_at)