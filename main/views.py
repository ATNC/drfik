# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    get_object_or_404,
    UpdateAPIView,
    GenericAPIView
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from main.models import Team
from main.permissions import IsHaveNotGotTeam, IsHaveGotTeam, IsNotAuthenticated
from main.token import registration_token, forgot_token
from main.serializers import (
    CreateUserSerializer,
    ForgotPasswordSerializer,
    LoginUserSerializer,
    SetPasswordSerializer,
    CreateTeamSerializer,
    InviteSerializer,
)


class RegisterUserView(CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = (IsNotAuthenticated, )

    def get_serializer_context(self):
        context = super(RegisterUserView, self).get_serializer_context()
        context['team'] = self.request.query_params.get('team')
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=self.request.data,
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if not user.is_active:
            token = registration_token.make_token(user)
            message = render_to_string('confirmation_email.html', {
                'site': get_current_site(self.request).domain,
                'token': token,
                'uid': urlsafe_base64_encode(force_bytes(user.pk))
            })
            send_mail(
                subject='Confirm your email',
                message=message,
                from_email='t998691@mvrht.net',
                recipient_list=[user.email]

            )
            return Response({'data': 'Check your email'}, status=status.HTTP_201_CREATED)
        else:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return Response({'url': reverse('main:create_team')}, status=status.HTTP_201_CREATED)


class LoginUserView(CreateAPIView):
    serializer_class = LoginUserSerializer
    permission_classes = (IsNotAuthenticated, )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        user = authenticate(username=email, password=password)
        if user and user.is_active:
            login(request, user)
            return JsonResponse(
                {'url': reverse('main:register_user')},
                status=status.HTTP_200_OK
            )
        else:
            return JsonResponse(
                {'error': 'Invalid user'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ForgotPasswordView(CreateAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = (IsNotAuthenticated, )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('email')

        token = forgot_token.make_token(user)

        message = render_to_string('confirmation_email.html', {
            'site': get_current_site(self.request).domain,
            'token': token,
            'uid': urlsafe_base64_encode(force_bytes(user.pk))
        })
        send_mail(
            subject='Forgot password',
            message=message,
            from_email='t998691@mvrht.net',
            recipient_list=[user.email]

        )
        return Response({'data': 'Check your email'}, status=status.HTTP_200_OK)


class ConfirmView(APIView):

    def get(self, request, uidb64, token):
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(get_user_model(), pk=uid)
        if registration_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)

            return JsonResponse(
                {'url': reverse('main:create_team')},
                status=status.HTTP_200_OK
            )
        else:
            return JsonResponse(
                {'error': 'Invalid user'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ForgotPasswordAccept(APIView):

    def get(self, request, uidb64, token):
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(get_user_model(), pk=uid)
        if forgot_token.check_token(user, token):
            new_password = get_user_model().objects.make_random_password()
            user.set_password(new_password)
            user.save()

            send_mail(
                subject='New password',
                message='New password is {}'.format(new_password),
                from_email='t998691@mvrht.net',
                recipient_list=[user.email]

            )

            return JsonResponse(
                {'url': reverse('main:login_user')},
                status=status.HTTP_200_OK
            )
        else:
            return JsonResponse(
                {'error': 'Invalid user'},
                status=status.HTTP_400_BAD_REQUEST
            )


class SetPasswordView(UpdateAPIView):
    serializer_class = SetPasswordSerializer
    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return self.request.user


class CreateTeamView(CreateAPIView):
    serializer_class = CreateTeamSerializer
    queryset = Team.objects.all()
    permission_classes = (IsAuthenticated, IsHaveNotGotTeam)

    def get_serializer_context(self):
        context = super(CreateTeamView, self).get_serializer_context()
        context['user'] = self.request.user
        return context


class InviteView(CreateAPIView):
    serializer_class = InviteSerializer
    permission_classes = (IsAuthenticated, IsHaveGotTeam)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        message = render_to_string('invite_email.html', {
            'site': get_current_site(self.request).domain,
            'username': request.user.username,
            'team': request.user.teams.first().name
        })
        send_mail(
            subject='Invite to {}'.format(get_current_site(self.request).domain),
            message=message,
            from_email='t998691@mvrht.net',
            recipient_list=[email, ]

        )
        return Response({'data': 'Email is sent'}, status=status.HTTP_200_OK)


class LogoutUserView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        logout(request)
        return Response({})
