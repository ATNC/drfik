from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model

from main.models import Team


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=get_user_model().objects.all())
        ]
    )
    password = serializers.CharField(
        min_length=6,
        write_only=True
    )

    def create(self, validated_data):
        nickname = validated_data.get('email')
        team = self.context.get('team', None)
        instance = self.Meta.model.objects.create_user(
            username=nickname,
            is_active=True if team else False,
            **validated_data
        )
        if team and Team.objects.filter(name=team).exists():
            team_instance = Team.objects.get(name=team)
            team_instance.members.add(instance)

        return instance

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'password',
            'first_name',
            'last_name',
        )


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = get_user_model().objects.filter(email=value).first()
        if user:
            return user
        else:
            raise serializers.ValidationError('Email is not exists')


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        min_length=6
    )


class SetPasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            'old_password',
            'new_password',
        )

    def update(self, instance, validated_data):
        if instance.check_password(validated_data.get('old_password')):
            instance.set_password(validated_data.get('new_password'))
            instance.save()
            return instance
        else:
            raise serializers.ValidationError('Invalid password')


class CreateTeamSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = Team
        fields = ('name', )

    def create(self, validated_data):
        user = self.context.get('user')
        name = validated_data.get('name')
        instance = Team.objects.create(
            name=name
        )
        instance.save()
        instance.members.add(user)
        return instance


class InviteSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError('Email is already exists')
        return value
