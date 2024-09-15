from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from bri_works_api.utils import get_content_from_s3, generate_qr_code

import pytz
import os

def send_invitation_email(subject, recipient_list, event, location, time, qr_code_data_list=None):
    ui_bri_work_icon_content = get_content_from_s3(image_key='static/ui-bri-work-icon.png')
    ui_bri_work_icon_image = MIMEImage(ui_bri_work_icon_content, _subtype="png")
    ui_bri_work_icon_image.add_header('Content-ID', '<briwork_icon>')
    html_content = render_to_string('event_invitation_email.html', {
      "event": event,
      "location": location,
      "time": time,
    })
    for i in range(len(recipient_list)):
      email = EmailMultiAlternatives(
          subject=subject,
          body=html_content,
          from_email=os.getenv('DEFAULT_FROM_EMAIL'),
          to=[recipient_list[i]]
      )
      email.attach_alternative(html_content, "text/html")
      email.attach(ui_bri_work_icon_image)
      
      qr_code_img = generate_qr_code(qr_code_data_list[i])
      qr_image = MIMEImage(qr_code_img.read(), _subtype='png')
      qr_image.add_header('Content-ID', '<qr_code>') 
      email.attach(qr_image)
      email.send()
    
def generate_time_string(start_time, end_time):
  wib_timezone = pytz.timezone('Asia/Jakarta')
  wib_start_time = start_time.astimezone(wib_timezone)
  wib_end_time = end_time.astimezone(wib_timezone)
  if wib_start_time.day != wib_end_time.day:
    wib_datetime_string = f'{wib_start_time.strftime("%d %B")} - {wib_end_time.strftime("%d %B")}'
    return wib_datetime_string
  wib_datetime_string = f'{wib_start_time.strftime("%d %B")} ({wib_start_time.strftime("%H:%M")} - {wib_end_time.strftime("%H:%M")})'
  return wib_datetime_string