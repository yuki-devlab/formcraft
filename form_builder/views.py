import logging

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import FormBuilderForm
from .services.formcraft import create_reception_system

logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
def builder_view(request):
    form = FormBuilderForm(request.POST or None)

    context = {
        "form": form,
        "result": None,
        "error_message": "",
    }

    if request.method == "GET":
        return render(
            request,
            "form_builder/index.html",
            context,
        )

    if not form.is_valid():
        return render(
            request,
            "form_builder/index.html",
            context,
        )

    try:
        result = create_reception_system(
            form_name=form.cleaned_data["form_name"],
            description=form.cleaned_data["description"],
            notification_emails=(
                form.cleaned_data["notification_emails"]
            ),
        )

    except Exception:
        logger.exception(
            "Googleフォームの作成に失敗しました。"
        )

        context["error_message"] = (
            "Googleフォームを作成できませんでした。"
            "時間を置いて再度お試しください。"
        )

        return render(
            request,
            "form_builder/index.html",
            context,
            status=500,
        )

    context["result"] = result

    return render(
        request,
        "form_builder/index.html",
        context,
    )