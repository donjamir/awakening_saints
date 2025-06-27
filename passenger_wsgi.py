import sys
import os

sys.path.insert(0, '/home/awakzfip/public_html')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecom.settings'  # Use your Django project package name here

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
