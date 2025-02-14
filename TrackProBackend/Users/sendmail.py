

from asgiref.sync import async_to_sync
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string,get_template
from django.utils.html import strip_tags
from channels.layers import get_channel_layer
from django.core.mail import EmailMessage
from django.shortcuts import render
from TrackProBackend.settings import EMAIL_HOST_USER
from .static_info import adminemail,hremail







@async_to_sync
async def send_async_custom_template_email(subject, data_dict, from_email, recipient_list, template_name):
    try:
        channel_layer = get_channel_layer()

        # Render the specified HTML template with data
        html_content = render_to_string(f'{template_name}', data_dict)
        text_content = strip_tags(html_content)  # Remove HTML tags for the plain text version

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list,
        )
        email.attach_alternative(html_content, "text/html")

        # Send the email without 'await'
        email.send()

    except Exception as e:


        try:        
            message = get_template(
                'failmail.html').render(data_dict)
            
            msg = EmailMessage(
                "Issue with Auto-Generated Application Notifications Application ID " + data_dict['applicationid'],
                message,
                EMAIL_HOST_USER,
                ['mahesh.kattale@onerooftech.com'],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
        except Exception as p:
            print('exception occured fot mail', p)

