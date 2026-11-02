from django.urls import path

from form_builder.views import builder_view

urlpatterns = [
    path("", builder_view, name="builder"),
]