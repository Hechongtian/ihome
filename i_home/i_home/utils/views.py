from urllib.parse import urlencode
from django.shortcuts import redirect


def get_html_file(request, file_name):
    if file_name != 'favicon.ico':
        file_name = "static/html/"+file_name

    params = request.GET
    if params:
        result = urlencode(params)
        return redirect(file_name+'?{}'.format(result))

    return redirect(file_name)

def index(request):
    return redirect('/static/html/index.html')