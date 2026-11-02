from django.urls import include, path

urlpatterns = [
    path("", include("form_builder.urls")),
]