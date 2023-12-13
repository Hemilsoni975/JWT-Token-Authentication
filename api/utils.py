from django.core.mail import send_mail
from django.conf import settings


def send_otp_email(email, otp):
    subject = 'Your OTP for Login'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def send_password_email(email, psd):
    subject = f'Your New Password For {email}'
    message = f'Your New Password : {psd} \n Please Dont Share your Password With Anyone!'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def success_true_response(message=None, data=None, count=None):
    result = dict(success=True)
    result['message'] = message or ''
    result['data'] = data or {}
    if count is not None:
        result['count'] = count
    return result


def success_false_response(message=None, data=None):
    result = dict(success=False)
    result['message'] = message or ''
    result['data'] = data or {}
    return result
