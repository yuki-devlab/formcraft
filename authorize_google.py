from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow


BASE_DIR = Path(__file__).resolve().parent

CLIENT_FILE = (
    BASE_DIR
    / ".secrets"
    / "google_oauth_client.json"
)

TOKEN_FILE = (
    BASE_DIR
    / ".secrets"
    / "google_token.json"
)

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
]


def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_FILE,
        SCOPES,
    )

    credentials = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(
        credentials.to_json(),
        encoding="utf-8",
    )

    print("Googleアカウントの認証が完了しました。")


if __name__ == "__main__":
    main()