from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import logging


class CustomPasswordValidator():
    def validate(self, password, user=None, username=None):
        if len(password) < 8:
            raise ValidationError(_("パスワードは最低8文字以上必要です。"))

        if username is not None and username.lower() in password.lower():
            logging.warning("パスワードにユーザー名が含まれています。")
            raise ValidationError(_("あなたの他の個人情報と似ているパスワードにはできません。"), code='password_contains_username')
        
        common_passwords = ['password', '123456', 'qwerty']
        if password.lower() in common_passwords:
            logging.warning("よく使われるパスワードです。")
            raise ValidationError(_("よく使われるパスワードにはできません。"), code='common_password')

        if password.isdigit():
            logging.warning("数字だけのパスワードです。")
            raise ValidationError(_("数字だけのパスワードにはできません。"), code='password_digits')

    def get_help_text(self):
        return _(
            "パスワードは最低8文字以上必要で、他の個人情報と似ていない、よく使われない、数字だけでないパスワードを使用してください。"
        )