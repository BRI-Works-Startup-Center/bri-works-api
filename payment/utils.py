import os
import hashlib

def verify_notification(order_id, status_code, gross_amount, signature_key):
  server_key = str(os.getenv('MIDTRANS_SERVER_KEY'))
  authenticity_string = f'{order_id}{status_code}{gross_amount}{server_key}'
  sha512 = hashlib.sha512()
  sha512.update(authenticity_string.encode('utf-8'))
  return sha512.hexdigest() == signature_key