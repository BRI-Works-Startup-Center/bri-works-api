from io import BytesIO

import boto3
import os
import qrcode

def get_content_from_s3(image_key):
    s3_client = boto3.client(
      's3',
      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
      region_name=os.getenv('AWS_S3_REGION_NAME')
    )
    
    response = s3_client.get_object(Bucket=os.getenv('AWS_STORAGE_BUCKET_NAME'), Key=image_key)
    print(os.getenv('AWS_STORAGE_BUCKET_NAME'))
    return response['Body'].read()

def generate_qr_code(data):
  qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
  )
  qr.add_data(data)
  qr.make(fit=True)

  img = qr.make_image(fill='black', back_color='white')
  img_byte_arr = BytesIO()
  img.save(img_byte_arr, format='PNG')
  img_byte_arr.seek(0)
  return img_byte_arr