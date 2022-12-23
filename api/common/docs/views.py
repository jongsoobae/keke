from functools import partial
from typing import Any, List, Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import path, reverse
from ninja import NinjaAPI
from ninja.conf import settings as ninja_settings
from ninja.openapi.urls import get_root_url
from ninja.openapi.views import openapi_json
from ninja.types import DictStrAny

render_swagger = ninja_settings.DOCS_VIEW == "swagger"
view_tpl = "ninja/swagger.html" if render_swagger else "ninja/redoc.html"
view_cdn_tpl = "swagger_cdn.html" if render_swagger else "../templates/ninja/redoc_cdn.html"


def openapi_view(request: HttpRequest, api: "NinjaAPI") -> HttpResponse:
    """
    I do not really want ninja to be required in INSTALLED_APPS for now
    so we automatically detect - if ninja is in INSTALLED_APPS - then we render with django.shortcuts.render
    otherwise - rendering custom html with swagger js from cdn
    """
    context = {
        "api": api,
        "openapi_json_url": reverse(f"{api.urls_namespace}:openapi-json"),
    }
    if "ninja" in settings.INSTALLED_APPS:
        return render(request, view_tpl, context)
    else:
        return openapi_view_cdn(request, context)


def openapi_view_cdn(request: HttpRequest, context: Optional[DictStrAny] = None) -> HttpResponse:
    import os

    from django.http import HttpResponse
    from django.template import RequestContext, Template

    tpl_file = os.path.join(os.path.dirname(__file__), view_cdn_tpl)
    with open(tpl_file) as f:
        tpl = Template(f.read())
    html = tpl.render(RequestContext(request, context))
    return HttpResponse(html)


def get_openapi_urls(api: "NinjaAPI") -> List[Any]:
    result = []

    if api.openapi_url:
        view = partial(openapi_json, api=api)
        if api.docs_decorator:
            view = api.docs_decorator(view)  # type: ignore
        result.append(
            path(api.openapi_url.lstrip("/"), view, name="openapi-json"),
        )

        assert api.openapi_url != api.docs_url, "Please use different urls for openapi_url and docs_url"

        if api.docs_url:
            view = partial(openapi_view, api=api)
            if api.docs_decorator:
                view = api.docs_decorator(view)  # type: ignore
            result.append(
                path(api.docs_url.lstrip("/"), view, name="openapi-view"),
            )

    return result


class NinjaSwaggerAPI(NinjaAPI):
    def __init__(self, *args, **kwargs):
        self.persist_auth = kwargs.pop("persist_auth", False) or False
        super().__init__(*args, **kwargs)

    def _get_urls(self):
        result = get_openapi_urls(self)

        for prefix, router in self._routers:
            result.extend(router.urls_paths(prefix))

        result.append(get_root_url(self))
        return result
