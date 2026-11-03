# FormCraft

必要な情報を入力するだけで、Googleフォーム・回答保存用のGoogleスプレッドシート・回答通知をまとめて設定できるWebアプリです。

## デモ

https://formcraft-jp.vercel.app/

## 主な機能

- Googleフォームの自動作成
- フォーム説明文の設定
- 以下の質問項目を自動追加
  - お名前
  - メールアドレス
  - お問い合わせ内容
- 回答保存用Googleスプレッドシートの作成
- Googleフォーム回答時のメール通知
- 最大10件の通知先メールアドレスに対応
- 作成したフォーム・編集画面・スプレッドシートのURL表示

## 使用技術

- Python
- Django 5.2
- Tailwind CSS
- Google Forms API
- Google Apps Script
- Vercel

## ローカルでの起動方法

### 1. リポジトリを取得

```bash
git clone https://github.com/yuki-devlab/formcraft.git
cd formcraft
```

### 2. 仮想環境を作成

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. パッケージをインストール

```bash
pip install -r requirements.txt
```

### 4. Google OAuth認証情報を配置

プロジェクト直下に次のファイルを配置します。

```text
.secrets/google_oauth_client.json
```

続いて認証処理を実行します。

```bash
python authorize_google.py
```

認証が完了すると、次のファイルが作成されます。

```text
.secrets/google_token.json
```

### 5. 環境変数を設定

```bash
export FORMCRAFT_APPS_SCRIPT_URL="Apps ScriptのウェブアプリURL"
export FORMCRAFT_APPS_SCRIPT_SECRET="共有シークレット"
export DJANGO_SECRET_KEY="Djangoのシークレットキー"
```

### 6. 開発サーバーを起動

```bash
python manage.py runserver
```

ブラウザで以下を開きます。

```text
http://127.0.0.1:8000/
```

## 環境変数

| 変数名 | 内容 |
| --- | --- |
| `DJANGO_SECRET_KEY` | Djangoで使用する秘密鍵 |
| `FORMCRAFT_APPS_SCRIPT_URL` | Apps ScriptのウェブアプリURL |
| `FORMCRAFT_APPS_SCRIPT_SECRET` | DjangoとApps Scriptで共有する秘密情報 |
| `GOOGLE_TOKEN_JSON` | Google OAuthトークンのJSON文字列 |

ローカル環境では、`GOOGLE_TOKEN_JSON`の代わりに`.secrets/google_token.json`を使用できます。

## 処理の流れ

1. ユーザーがフォーム名・説明文・通知先を入力
2. DjangoからGoogle Forms APIを呼び出す
3. Googleフォームと質問項目を作成
4. Apps Scriptで回答保存用スプレッドシートを作成
5. 回答通知用トリガーを設定
6. 作成した各URLを画面に表示

## 注意事項

次の情報はGitHubへ公開しないでください。

- `.secrets/`
- `.env`
- Google OAuthトークン
- 共有シークレット
- Djangoのシークレットキー

また、このアプリを一般公開すると、第三者が開発者のGoogleアカウントを利用してフォームを作成できる状態になります。公開時は、認証・回数制限・Bot対策などを追加してください。

## ライセンス

個人開発プロジェクトです。