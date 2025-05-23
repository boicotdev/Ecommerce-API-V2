from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import status
from rest_framework.response import Response


def send_email(subject, email, recipient_list, context, template_url: str = "email/newsletter-subscription.html",
               success_message='Email send successfully'):
    # Preparar y enviar el correo
    subject = subject
    context = context
    html_content = render_to_string(template_url, context)
    text_content = strip_tags(html_content)
    try:
        email_msg = EmailMultiAlternatives(
            subject,
            text_content,
            "no-reply@avoberry.com",
            [email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()

        return Response(
            {"message": success_message},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": f"No se pudo enviar el correo: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
