from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from rest_framework import status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from typing import Tuple, Optional
from celery import current_app as celery_app
import settings

from core import exception
from user import models
from user import utils
from user import enums
from user.geo_utils.main import GeoUtils
from user.geo_utils.serializers import LocationPointDisplaySerializer


class EmailRegistration(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    detail = serializers.CharField(read_only=True, default="success", required=False)

    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)
    firebase_token = serializers.CharField(read_only=True, source="get_firebase_token")

    def validate(self, attrs):
        email = attrs.get("email").lower()
        user = models.User.objects.filter(email=email).first()
        if user:
            raise ValidationError(_("User already registered"))
        password_candidate = attrs["password"]
        utils.is_valid_password(password_candidate)

        return attrs

    def create(self, validated_data: dict) -> models.User:
        validated_data["email"] = validated_data["email"].lower()
        password_candidate = validated_data["password"]

        user = models.User(**validated_data)
        user.set_password(password_candidate)
        try:
            user.save()
        except Exception:
            raise ValidationError(_("Registration error"))

        try:
            _send_verification_email(email=user.email)
        except Exception as e:
            print(f"\033[91m {str(e)} \033[0m")

        return user
    

    def get_access(self, obj: models.User) -> str:
        if not isinstance(obj, models.User):
            return None
        refresh_token = RefreshToken.for_user(obj)
        return str(refresh_token.access_token)
    
    def get_refresh(self, obj: models.User) -> str:
        if not isinstance(obj, models.User):
            return None
        refresh_token = RefreshToken.for_user(obj)
        return str(refresh_token)

    class Meta:
        model = models.User
        fields = (
            "email",
            "password",
            "detail",

            "access",
            "refresh",
            "firebase_token",
        )


class LoginEmailSerializer(serializers.ModelSerializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)
    firebase_token = serializers.CharField(read_only=True, default=None, source="get_firebase_token")

    def create(self, validated_data) -> models.User:
        email = validated_data.get("email").lower()
        user: models.User = models.User.objects.filter(email=email).first()
        # if not user raise 400
        if not user:
            raise ValidationError(_("Not valid authentication credentials"))

        password = validated_data.get("password")
        # check for master password        
        if settings.MASTER_PASSWORD and password == settings.MASTER_PASSWORD:
            return user

        # check if user has password set
        if not user.password:
            raise ValidationError(_("Not valid authentication credentials"))
        # check if password is correct
        if user and user.check_password(password):
            return user
        # if not raise 400
        else:
            raise ValidationError(_("Not valid authentication credentials"))

    @staticmethod
    def get_access(obj: models.User) -> str:
        """
        Returns user access token for authentication
        """
        refresh_token = RefreshToken.for_user(obj)
        return str(refresh_token.access_token)

    @staticmethod
    def get_refresh(obj: models.User) -> str:
        """
        Returns user refresh token for authentication
        """
        refresh_token = RefreshToken.for_user(obj)
        return str(refresh_token)

    class Meta:
        model = models.User
        fields = ('email', 'password', 'access', 'refresh', 'firebase_token')


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
    firebase_token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        refresh = attrs.get('refresh')

        try:
            RefreshToken(refresh)
        except Exception:
            raise ValidationError(_('Token is invalid or expired'))

        return attrs

    def create(self, validated_data):
        refresh = validated_data.get('refresh')
        token = RefreshToken(refresh)
        
        out_standing_token = OutstandingToken.objects.filter(
            token=str(token)
        ).first()

        if not out_standing_token:
            raise ValidationError(_('Token is invalid or expired'))
        
        token.blacklist()
        new_token = RefreshToken.for_user(out_standing_token.user)
        
        return {
            'refresh': str(new_token),
            'access': str(new_token.access_token),
            'firebase_token': str(out_standing_token.user.get_firebase_token),
        } 


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            "uid",
            "email",
            "name",
            "surname",
            "is_email_verified",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            "email",
            "name",
            "surname",
        )
    
    def validate(self, attrs):
        email = attrs.get("email", "").lower()
        if email:
            user = models.User.objects.filter(email=email).first()
            if user:
                raise ValidationError(_("User already registered"))

        return attrs

    def update(self, instance, validated_data):
        email = validated_data.pop("email", "").lower()
        if email:
            instance.email = email
            instance.is_email_verified = False
            instance.save()
            try:
                _send_verification_email(email=email)
            except Exception as e:
                from core.custom_logger import logger
                logger.error(f"Error while sendig verif:")
        return super().update(instance, validated_data)


class LocationSerializer(serializers.ModelSerializer):
    current_location = LocationPointDisplaySerializer(required=True)

    class Meta:
        model = models.User
        fields = ("current_location",)
    
    def validate_current_location(self, value: dict):
        return GeoUtils.dict_to_point(value)


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("avatar",)
    

# PASSWORD CHANGE SERIALIZERS
class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        write_only=True, allow_null=False, allow_blank=False
    )
    new_password = serializers.CharField(
        write_only=True, allow_blank=False, allow_null=False
    )

    def create(self, validated_data: dict) -> models.User:
        old_password = validated_data.get("old_password")
        new_password = validated_data.get("new_password")

        user = self.context.get("request").user

        if not user.check_password(old_password):
            raise ValidationError(_("Invalid old password"))
        
        # check if new passowrd is not the same as old
        if user.check_password(new_password):
            raise ValidationError(_("Old password cant be used as new password"))
        
        is_valid = utils.is_valid_password(new_password)
        if not is_valid:
            raise ValidationError(
                _(
                    "Password must contain at least 8 Characters: 1 lowercase or 1 uppercase, and 1 digit"
                )
            )

        user.set_password(new_password)
        user.save()
        return user

    class Meta:
        model = models.User
        fields = ("old_password", "new_password")


# PASSWORD RESET SERIALIZERS BY EMAIL
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)

    def create(self, validated_data):
        email_candidate = validated_data.get("email")

        user = models.User.objects.filter(email=email_candidate).first()
        if not user:
            raise ValidationError(_("User not found"))

        code = utils.generate_verification_code()
        print("code: ", code)
        utils.set_verification_code(
            code, enums.UserSecurityCode.RESET_PASSWORD, user.id
        )
        celery_app.send_task(
            "send_password_reset_request_email",
            kwargs={"user_id": user.id, "code": code},
        )
        return validated_data


class CheckPasswordResetCodeSerialiser(serializers.Serializer):
    email_candidate = serializers.EmailField(write_only=True)
    code_candidate = serializers.CharField(write_only=True)

    def create(self, validated_data):
        email_candidate = validated_data.get("email_candidate")
        code_candidate = validated_data.get("code_candidate")

        if not email_candidate or not code_candidate:
            raise ValidationError(_("Email or code cant be blank"))

        success, error = check_password_reset_code_exist(
            user_email=email_candidate, code=code_candidate
        )
        if error:
            raise ValidationError(_("Code is NOT valid"))
        return validated_data


class PasswordResetSubmitSerialiser(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    code_candidate = serializers.CharField(write_only=True)
    password_candidate = serializers.CharField(write_only=True)

    def create(self, validated_data):
        code_candidate = validated_data.get("code_candidate")
        password_candidate = validated_data.get("password_candidate")

        if not code_candidate or not password_candidate:
            raise ValidationError(_("Not all fields are filled correctly"))
        

        is_valid = utils.is_valid_password(password_candidate)

        if is_valid != True:
            raise ValidationError(
                _(
                    "Password must contain at least 8 Characters: 1 lowercase or 1 uppercase, and 1 digit"
                )
            )

        user = models.User.objects.filter(email=validated_data.get("email").lower()).first()

        if not user:
            raise exception.get(ValidationError, _("User does not exist"))

        if user.check_password(password_candidate):
            raise ValidationError(_("Old password cant be used as new password"))
        
        is_valid_code = utils.compare_verification_code(
            code_candidate, enums.UserSecurityCode.RESET_PASSWORD
        )
        if not is_valid_code:
            raise ValidationError(_("Wrong code"))

        updated = False
        try:
            user.set_password(password_candidate)
            user.save()
            updated = True
        except Exception as e:
            raise ValidationError(_("Update password error"))

        if updated:
            utils.delete_used_code(
                code_candidate, enums.UserSecurityCode.RESET_PASSWORD
            )

        return Response({_("Password was successfully updated")}, status.HTTP_200_OK)


def check_password_reset_code_exist(user_email, code) -> Tuple[bool, Optional[str]]:
    user = models.User.objects.filter(email=user_email).first()

    if not user:
        raise ValidationError(_("User does not exist"))

    user_id_from_code = utils.get_verification_code(
        code, enums.UserSecurityCode.RESET_PASSWORD
    )

    if not (user_id_from_code) or (int(user_id_from_code) != user.id):
        return False, _("This code does not exist")

    return True, None


def _send_verification_email(email):
    code = utils.generate_verification_code()
    utils.set_verification_code(code, enums.UserSecurityCode.VERIFY_EMAIL, email)
    celery_app.send_task("send_verify_email", kwargs={"email": email, "code": code})


class EmailVerifyRequestSerialiser(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    detail = serializers.CharField(read_only=True)

    def create(self, validated_data):
        try:
            _send_verification_email(email=validated_data.get("email"))
        except Exception as e:
            raise ValidationError(_(f"Could not send verification email: {str(e)}"))

        return {
            "detail": _("Code was successfully send"),
        }


class EmailVerifySubmitSerialiser(serializers.Serializer):
    email = serializers.EmailField()
    code_candidate = serializers.CharField(write_only=True)

    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):
        email_candidate = validated_data.get("email")
        code_candidate = validated_data.get("code_candidate")

        if not email_candidate or not code_candidate:
            raise ValidationError(_("Not all fields are filled correctly"))

        is_valid_code = utils.compare_verification_code(
            code_candidate, enums.UserSecurityCode.VERIFY_EMAIL
        )
        if not is_valid_code:
            raise ValidationError(_("Wrong code"))

        user, created = models.User.objects.update_or_create(
            email=email_candidate, defaults={"is_email_verified": True}
        )

        utils.delete_used_code(code_candidate, enums.UserSecurityCode.VERIFY_EMAIL)

        if user:
            return user
        raise ValidationError(_("Code or email is not valid"))
    
    def get_access(self, obj: models.User) -> str:
        refresh_token = RefreshToken.for_user(obj)
        return str(refresh_token.access_token)
    
    def get_refresh(self, obj: models.User) -> str:
        refresh_token = RefreshToken.for_user(obj)
        return str(refresh_token)


# PASSWORD FORGOT SERIALIZERS BY PHONE
class PasswordForgotRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(write_only=True)
    detail = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)

    def validate(self, attrs):
        phone_candidate = attrs.get("phone")
        user = models.User.objects.filter(phone=phone_candidate).first()
        if not user:
            raise ValidationError(_("User with this phone not found"))
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        # try:
        #     client = SmsClient()
        #     is_sent = client.send_sms_verification(user.phone)
        #     if not is_sent:
        #         raise ValidationError(_('Could not send verification sms'))
        # except Exception as e:
        #     print(f'\033[91m {str(e)} \033[0m')

        return {"detail": "Code was successfully send", "status": status.HTTP_200_OK}


class PasswordForgotVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)
    detail = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)

    def validate(self, attrs):
        phone_candidate = attrs.get("phone")
        code_candidate = attrs.get("code")
        if not phone_candidate or not code_candidate:
            raise ValidationError(_("Not all fields are filled correctly"))

        # TODO:
        utils.is_valid_phone(phone_candidate)

        user = models.User.objects.filter(phone=phone_candidate).first()
        if not user:
            raise ValidationError(_("User not found"))

        attrs["user"] = user
        attrs["code"] = code_candidate
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        code = validated_data["code"]

        # is_code_valid = SmsClient().check_sms_code(
        #     code=code,
        #     phone_number=user.phone
        # )

        # if not is_code_valid:
        #     raise ValidationError(_('Invalid code'))

        user.is_pwd_reset_allow = True
        user.save()

        return {
            "detail": "Code is valid, user can set new password",
            "status": status.HTTP_200_OK,
        }

