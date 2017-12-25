# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth import get_user_model


class Team(models.Model):
    name = models.CharField(max_length=64, unique=True)
    members = models.ManyToManyField(get_user_model(), related_name='teams')
