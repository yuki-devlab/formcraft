from django import forms

class FormBuilderForm(forms.Form):
    form_name = forms.CharField(
        label="フォーム名",
        max_length=100,
    )

    description = forms.CharField(
        label="説明文",
        max_length=500,
        required=False,
        widget=forms.Textarea,
    )

    notification_emails = forms.CharField(
        label="通知先メールアドレス",
        max_length=2558,
    )

    def clean_notification_emails(self):
        value = self.cleaned_data["notification_emails"]

        emails = []
        seen = set()

        for item in value.split(","):
            email = item.strip().lower()

            if not email or email in seen:
                continue

            forms.EmailField().clean(email)
            seen.add(email)
            emails.append(email)

        if not emails:
            raise forms.ValidationError(
                "通知先メールアドレスを入力してください。"
            )

        if len(emails) > 10:
            raise forms.ValidationError(
                "通知先メールアドレスは、最大10件まで入力できます。"
            )

        return emails