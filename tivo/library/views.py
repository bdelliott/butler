from django.shortcuts import render_to_response
from django.template.context import RequestContext

from sync.models import LibraryItem

def index(request):
    """Generate index view of the library of shows."""

    # TODO this should probably be a custom manager method
    items = LibraryItem.objects.filter(h264=True).order_by('-show__date')

    context = RequestContext(request)
    context["items"] = items
    return render_to_response("library/index.html", context)
