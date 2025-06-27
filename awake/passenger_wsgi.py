import sys
import os

sys.path.insert(0, ' /home/awakzfip/awakeningsaints.org/awake')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecom.settings'  # adjust if your project folder has a different name

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
