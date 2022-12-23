from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

from api.common.docs.views import NinjaSwaggerAPI

api = NinjaSwaggerAPI(csrf=False, auth=None, version="1", persist_auth=True)


@api.get("/ping", auth=None)
def ping(request):
    return "pong"


urlpatterns = [path("", lambda req: redirect("/api/docs")), path("admin/", admin.site.urls), path("api/", api.urls)]
