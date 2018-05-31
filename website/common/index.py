from simplerr.web import web

@web('/common/static/<path:file>', file=True)
def files(request, file):
    return './common/static/' + file
