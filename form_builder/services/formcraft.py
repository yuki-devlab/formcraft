import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from google.auth.transport.requests import (
    Request as GoogleRequest,
)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
]

TOKEN_FILE = (
    settings.BASE_DIR
    / ".secrets"
    / "google_token.json"
)


def load_credentials():
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            "google_token.jsonが見つかりません。"
            "先にauthorize_google.pyを実行してください。"
        )

    credentials = Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES,
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(GoogleRequest())

        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    if not credentials.valid:
        raise RuntimeError(
            "Googleの認証情報が無効です。"
        )

    return credentials


def create_text_question(
    *,
    title,
    index,
    paragraph=False,
    required=True,
):
    return {
        "createItem": {
            "item": {
                "title": title,
                "questionItem": {
                    "question": {
                        "required": required,
                        "textQuestion": {
                            "paragraph": paragraph,
                        },
                    },
                },
            },
            "location": {
                "index": index,
            },
        },
    }


def build_update_requests(description):
    requests = []

    if description:
        requests.append(
            {
                "updateFormInfo": {
                    "info": {
                        "description": description,
                    },
                    "updateMask": "description",
                },
            }
        )

    requests.extend(
        [
            create_text_question(
                title="お名前",
                index=0,
            ),
            create_text_question(
                title="メールアドレス",
                index=1,
            ),
            create_text_question(
                title="お問い合わせ内容",
                index=2,
                paragraph=True,
            ),
        ]
    )

    return requests

def create_response_spreadsheet(
    *,
    form_id,
    form_name,
    notification_emails,
):
    web_app_url = (
        settings.FORMCRAFT_APPS_SCRIPT_URL
    )

    shared_secret = (
        settings.FORMCRAFT_APPS_SCRIPT_SECRET
    )

    if not web_app_url:
        raise RuntimeError(
            "Apps ScriptのURLが未設定です。"
        )

    if not shared_secret:
        raise RuntimeError(
            "Apps Scriptの共有シークレットが"
            "未設定です。"
        )

    request_body = json.dumps(
        {
            "secret": shared_secret,
            "formId": form_id,
            "formName": form_name,
            "notificationEmails": notification_emails,
        }
    ).encode("utf-8")

    request = Request(
        web_app_url,
        data=request_body,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(
            request,
            timeout=60,
        ) as response:
            response_text = (
                response
                .read()
                .decode("utf-8")
            )
    except (
        HTTPError,
        URLError,
        TimeoutError,
    ) as error:
        raise RuntimeError(
            "Apps Scriptへの接続に失敗しました。"
        ) from error

    try:
        response_data = json.loads(
            response_text
        )
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Apps Scriptから不正な応答が"
            "返されました。"
        ) from error

    if not response_data.get("ok"):
        error_code = response_data.get(
            "error",
            "unknown_error",
        )

        raise RuntimeError(
            "Apps Scriptの処理に失敗しました。"
            f" code={error_code}"
        )

    spreadsheet_id = response_data.get(
        "spreadsheetId"
    )

    spreadsheet_url = response_data.get(
        "spreadsheetUrl"
    )

    if not spreadsheet_id or not spreadsheet_url:
        raise RuntimeError(
            "スプレッドシート情報が"
            "応答に含まれていません。"
        )

    return {
        "spreadsheet_id": spreadsheet_id,
        "spreadsheet_url": spreadsheet_url,
    }

def create_reception_system(
    *,
    form_name,
    description,
    notification_emails,
):
    credentials = load_credentials()

    forms_service = build(
        "forms",
        "v1",
        credentials=credentials,
        cache_discovery=False,
    )

    created_form = (
        forms_service.forms()
        .create(
            body={
                "info": {
                    "title": form_name,
                },
            },
            unpublished=True,
        )
        .execute()
    )

    form_id = created_form["formId"]

    update_requests = build_update_requests(
        description=description,
    )

    forms_service.forms().batchUpdate(
        formId=form_id,
        body={
            "requests": update_requests,
        },
    ).execute()

    spreadsheet = create_response_spreadsheet(
        form_id=form_id,
        form_name=form_name,
        notification_emails=notification_emails,
    )

    forms_service.forms().setPublishSettings(
        formId=form_id,
        body={
            "publishSettings": {
                "publishState": {
                    "isPublished": True,
                    "isAcceptingResponses": True,
                },
            },
            "updateMask": "publishState",
        },
    ).execute()

    form = (
        forms_service.forms()
        .get(formId=form_id)
        .execute()
    )

    return {
        "form_name": form_name,
        "form_url": form["responderUri"],
        "edit_url": (
            "https://docs.google.com/forms/d/"
            f"{form_id}/edit"
        ),
        "spreadsheet_url": (
            spreadsheet["spreadsheet_url"]
        ),
    }