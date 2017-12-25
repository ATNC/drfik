# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail

from main.models import Team
from main.token import registration_token, forgot_token


class UserTest(APITestCase):

    def setUp(self):
        self.User = get_user_model()
        self.register_user_url = reverse('main:register_user')
        self.registration_test_data = {
            'email': 'testemail@gmail.com',
            'password': 'qweqweqwe',
            'first_name': 'Anton',
            'last_name': 'Alabajev'
        }
        self.test_user = self.User.objects.create_user(
            email='azaza@gmail.com',
            username='azaza@gmail.com',
            password='qweqweqwe',
        )

    def test_register_user(self):
        returned_data = {
            'data': 'Check your email'

        }
        response = self.client.post(
            self.register_user_url,
            data=self.registration_test_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.User.objects.count(), 2)
        self.assertDictEqual(response.data, returned_data)

        # test email sending
        self.assertEqual(mail.outbox[0].subject, 'Confirm your email')

    def test_register_user_with_duplicate_email(self):
        self.client.post(
            self.register_user_url,
            data=self.registration_test_data
        )
        response = self.client.post(
            self.register_user_url,
            data=self.registration_test_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.User.objects.count(), 2)
        self.assertTrue(response.data.get('email'))

    def test_register_user_and_confirm_email(self):
        self.client.post(
            self.register_user_url,
            data=self.registration_test_data
        )
        user = get_user_model().objects.latest('id')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = registration_token.make_token(user)
        confirm_url = reverse('main:confirm', kwargs={
            'uidb64': uid,
            'token': token
        })
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_user_and_forgot_password(self):
        self.client.post(
            self.register_user_url,
            data=self.registration_test_data
        )
        response = self.client.post(
            reverse('main:forgot_password'),
            data={
                'email': self.registration_test_data.get('email')
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = get_user_model().objects.latest('id')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = forgot_token.make_token(user)
        forgot_password_accept_url = reverse('main:forgot_password_accept', kwargs={
            'uidb64': uid,
            'token': token
        })
        response = self.client.get(forgot_password_accept_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test email
        self.assertEqual(mail.outbox[-1].subject, 'New password')

    def test_login_user(self):
        login_data = {
            'email': self.test_user.email,
            'password': 'qweqweqwe',
        }
        response = self.client.post(
            reverse('main:login_user'),
            data=login_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_user_with_incorrect_password(self):
        login_data = {
            'email': self.test_user.email,
            'password': 'qweqweqwe1',
        }
        response = self.client.post(
            reverse('main:login_user'),
            data=login_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_user_password(self):
        login_data = {
            'email': self.test_user.email,
            'password': 'qweqweqwe',
        }
        response = self.client.post(
            reverse('main:login_user'),
            data=login_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(
            reverse('main:set_password'),
            data={
                'old_password': 'qweqweqwe',
                'new_password': 'new_password',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_user_password_with_invalid_old_password(self):
        login_data = {
            'email': self.test_user.email,
            'password': 'qweqweqwe',
        }
        response = self.client.post(
            reverse('main:login_user'),
            data=login_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(
            reverse('main:set_password'),
            data={
                'old_password': 'qweqweqwe11',
                'new_password': 'new_password',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_team(self):
        login_data = {
            'email': self.test_user.email,
            'password': 'qweqweqwe',
        }
        response = self.client.post(
            reverse('main:login_user'),
            data=login_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            reverse('main:create_team'),
            data={
                'name': 'name'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 1)

    def test_create_another_team(self):
        login_data = {
            'email': self.test_user.email,
            'password': 'qweqweqwe',
        }
        response = self.client.post(
            reverse('main:login_user'),
            data=login_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.post(
            reverse('main:create_team'),
            data={
                'name': 'name'
            }
        )
        response = self.client.post(
            reverse('main:create_team'),
            data={
                'name': 'name2'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Team.objects.count(), 1)

    def test_invite_to_platform(self):
        login_data = {
            'email': self.test_user.email,
            'password': 'qweqweqwe',
        }
        response = self.client.post(
            reverse('main:login_user'),
            data=login_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.post(
            reverse('main:create_team'),
            data={
                'name': 'name'
            }
        )
        response = self.client.post(
            reverse('main:invite'),
            data={'email': 'test@gmail.com'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invite_to_platform_and_register_in_team(self):
            login_data = {
                'email': self.test_user.email,
                'password': 'qweqweqwe',
            }
            response = self.client.post(
                reverse('main:login_user'),
                data=login_data
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.client.post(
                reverse('main:create_team'),
                data={
                    'name': 'name'
                }
            )
            response = self.client.post(
                reverse('main:invite'),
                data={'email': 'testemail@gmail.com'}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.client.get(reverse('main:logout_user'))
            response = self.client.post(
                self.register_user_url + '?team=name',
                data={
                    'email': 'testemail2@gmail.com',
                    'password': 'qweqweqwe',
                }
            )
            user = self.User.objects.filter(
                email='testemail2@gmail.com',
                teams__name='name'
            ).exists()
            self.assertTrue(user)




