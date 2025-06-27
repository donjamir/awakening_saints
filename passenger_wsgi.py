import sys
import os

sys.path.insert(0, '/home/awakzfip/awakening_saints')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecom.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
