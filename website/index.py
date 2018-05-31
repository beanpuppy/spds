#!/usr/bin/python3.6
from simplerr.web import web
from common.models.main import *

@web('/', '/index.html')
def index(request):
    """Render homepage."""

@web('/404', '/404.html')
def error404(request):
    return {'title': '404'}

@web('/favicon.ico', file=True)
def favicon(request):
    return "./common/static/img/favicon.ico"
