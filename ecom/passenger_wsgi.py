import os
import sys

# Add your project directory to the sys.path
sys.path.insert(0, '/home/ssebadduka/awakening_saints')

# Set the settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecom.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
