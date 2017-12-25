from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class RegisterToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) +
            six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


class ForgotToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) +
            six.text_type(timestamp)
        )


registration_token = RegisterToken()
forgot_token = ForgotToken()
