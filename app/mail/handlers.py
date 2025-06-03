import os
import settings
from typing import Optional

from django.core.mail import EmailMultiAlternatives
# from anymail.message import attach_inline_image_file, attach_inline_image


from mail.models import Mail, MailLogo
from user.models import User


def get_logo_url() -> str:
    logo = MailLogo.objects.filter(is_default=True).first()
    if logo:
        return logo.logo.url
    return ''


# ------------  Single sender ------------- #
def single_sender_wrapper(subject: str, body: str, raw_text: str, email: str, name: Optional[str] = '') -> bool:
    """
        Sender wrapper
    """
    # Validate the recipient format
    if name:
        # Ensure the name is not an email address
        if '@' in name:
            # Invalid name (contains '@'), fallback to email only
            recipient = email
        else:
            recipient = f'{name} <{email}>'
    else:
        recipient = email

    print('recipient: ', recipient)  # Fixed typo: "recepient" → "recipient"

    # Message object
    msg = EmailMultiAlternatives(
        subject,
        raw_text,
        settings.DEFAULT_EMAIL_FROM,
        [recipient],  # Use validated recipient
    )
    msg.attach_alternative(body, 'text/html')

    # Send email
    try:
        msg.send()
        return True, None
    except Exception as e:
        print('Error: ', e)
        return False, str(e)


# --------------  Helpers ---------------- #
def body_replace(body, variables):
    """
       Replace variables in templates
    """
    new_body = body
    for key, value in variables.items():
        new_body = new_body.replace(str(key), str(value))
    return new_body


def create_model(
    subject: str,
    body: str,
    email: str,
    user: Optional[User] = None,
    code: str = None
) -> Mail:
    """
       Create Mail model
    """
    mail = Mail.objects.create(
        user=user,
        subject=subject,
        body=body,
        email=email,
        code=code,
    )
    mail.save()
    return mail


# --------------  Handlers ---------------- #
def verify_email_handler(email: str, code: str, url=f'{settings.FRONTEND_VERIFY_EMAIL_URL}'):
    """
       Send verification code for verify email
    """
    SUBJECT = f'Verify you email for {settings.PROJECT_NAME}'
    TEMPLATE = 'mail/templates/verify_email.html'

    # Load the email template
    with open(TEMPLATE, 'r') as f:
        body = f.read()

    # Variables for replace
    variables = {
        '{{code}}': code,
        '{{url}}': url,
        '{{logo}}': get_logo_url(),
    }

    body = body_replace(body, variables)

    mail = create_model(SUBJECT, body, email, user=None, code=code)

    res, error = single_sender_wrapper(
        SUBJECT,
        body,
        "Verify your email",
        email,
        f'{email}'
    )

    if res:
        mail.is_send = True
        mail.save()
    else:
        mail.error = error
        mail.save()
    

def password_reset_request_handler(user: User, code: str, url=f'{settings.FRONTEND_VERIFY_EMAIL_URL}'):
    """
       Send verification code for reset password
    """
    SUBJECT = f'Reset your password for {settings.PROJECT_NAME}'
    TEMPLATE = 'mail/templates/reset_password.html'

    # Load the email template
    with open(TEMPLATE, 'r') as f:
        body = f.read()

    # Variables for replace
    variables = {
        '{{code}}': code,
        '{{url}}': url,
        '{{logo}}': get_logo_url(),
    }

    body = body_replace(body, variables)

    mail = create_model(SUBJECT, body, user.email, user)

    res, error = single_sender_wrapper(
        SUBJECT,
        body, 
        "Reset your password",
        user.email,
        f'{user.name} {user.surname}'
    )

    if res:
        mail.is_send = True
        mail.save()
    else:
        mail.error = error
        mail.save()
