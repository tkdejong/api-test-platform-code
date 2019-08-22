from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from rest_framework.authtoken.models import Token


class CustomToken(Token):
    # key is no longer primary key, but still indexed and unique
    key = models.CharField(_("Key"), max_length=40, db_index=True, unique=True)
    # relation to user is a ForeignKey, so each user can have more than one token
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='auth_tokens',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    name = models.CharField(_("Name"), max_length=64)
    # created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        unique_together = (('user', 'name'),)

