from django.views.decorators.csrf import csrf_exempt
from json import loads
from django.db import connection
from django.http import JsonResponse
from posts_app.enquiry.enquiry import *
import psycopg2


@csrf_exempt
def notFound(request):
	return JsonResponse(thread, status = 200)
