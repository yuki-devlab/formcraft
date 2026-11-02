from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


BASE_DIR = Path(__file__).resolve().parent

TOKEN_FILE = (
    BASE_DIR
    / ".secrets"
    / "google_token.json"
)

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
]


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
        credentials.refresh(Request())

        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    if not credentials.valid:
        raise RuntimeError(
            "Googleの認証情報が無効です。"
        )

    return credentials


def main():
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
                    "title": "FormCraft APIテスト",
                }
            },
            unpublished=True,
        )
        .execute()
    )

    form_id = created_form["formId"]

    update_body = {
        "requests": [
            {
                "updateFormInfo": {
                    "info": {
                        "description": (
                            "必要事項を入力して送信してください。"
                        ),
                    },
                    "updateMask": "description",
                },
            },
            {
                "createItem": {
                    "item": {
                        "title": "お名前",
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {
                                    "paragraph": False,
                                },
                            },
                        },
                    },
                    "location": {
                        "index": 0,
                    },
                },
            },
            {
                "createItem": {
                    "item": {
                        "title": "メールアドレス",
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {
                                    "paragraph": False,
                                },
                            },
                        },
                    },
                    "location": {
                        "index": 1,
                    },
                },
            },
            {
                "createItem": {
                    "item": {
                        "title": "お問い合わせ内容",
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {
                                    "paragraph": True,
                                },
                            },
                        },
                    },
                    "location": {
                        "index": 2,
                    },
                },
            },
        ],
    }

    forms_service.forms().batchUpdate(
        formId=form_id,
        body=update_body,
    ).execute()

    forms_service.forms().setPublishSettings(
        formId=form_id,
        body={
            "publishSettings": {
                "publishState": {
                    "isPublished": True,
                    "isAcceptingResponses": True,
                }
            },
            "updateMask": "publishState",
        },
    ).execute()

    form = (
        forms_service.forms()
        .get(formId=form_id)
        .execute()
    )

    print("Googleフォームを作成しました。")
    print(f"フォームID: {form_id}")
    print(f"回答用URL: {form['responderUri']}")
    print(
        "編集用URL: "
        f"https://docs.google.com/forms/d/{form_id}/edit"
    )


if __name__ == "__main__":
    try:
        main()
    except HttpError as error:
        print("Google Forms APIでエラーが発生しました。")
        print(error)