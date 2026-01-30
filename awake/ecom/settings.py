from pathlib import Path
import os

# import pymysql     # This should be installed dependency on namecheap's ssh terminal
# pymysql.install_as_MySQLdb()   


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-ev28k=ir#vah2v)!-*t65t!+b#j(xnk24fv88!nkoemy)#0ag1'

DEBUG = True

ALLOWED_HOSTS = []

# DEBUG = False

# ALLOWED_HOSTS = ['awakeningsaints.org', '*']



INSTALLED_APPS = [
    
    'jazzmin',
    'django_ckeditor_5',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ecomapp.apps.EcomappConfig',
    'useraccounts.apps.UseraccountsConfig',
    'basketapp.apps.BasketappConfig',

    
]

AUTHENTICATION_BACKENDS = ['useraccounts.auth_backends.EmailAuthBackend',  # <-- use your correct path
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Optional: custom CSS for CKEditor styling in admin
CKEDITOR_5_CUSTOM_CSS = 'css/ckeditor_custom.css'

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            {
                'name': 'styles',
                'items': [
                    'heading', 'bold', 'italic', 'underline', 'strikethrough',
                    'link', 'blockquote', 'code', 'codeBlock',
                ],
            },
            {
                'name': 'lists',
                'items': [
                    'bulletedList', 'numberedList', 'todoList',
                ],
            },
            {
                'name': 'alignment',
                'items': [
                    'alignment:left', 'alignment:center',
                    'alignment:right', 'alignment:justify',
                ],
            },
            {
                'name': 'insert',
                'items': [
                    'imageUpload', 'mediaEmbed', 'insertTable', 'horizontalLine',
                ],
            },
            {
                'name': 'undo',
                'items': ['undo', 'redo'],
            },
        ],
        'blockToolbar': ['paragraph', 'heading1', 'heading2', 'heading3', 'heading4'],

        # Image toolbar when image is selected
        'image': {
            'toolbar': [
                'imageTextAlternative',    # Alt text
                'imageStyle:200px',         # Full width
                'imageStyle:side',         # Side aligned
                'imageStyle:alignLeft',
                'imageStyle:alignRight',
                'imageStyle:alignCenter',
                'imageRemove',             # Delete/remove image
            ]
        },

        # Table toolbar
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties'
            ]
        },

        # Alignment options
        'alignment': {
            'options': ['left', 'center', 'right', 'justify']
        },

        # Editor dimensions
        'height': 400,
        'width': '100%',
        'placeholder': 'Write text here...'
    },
}

ROOT_URLCONF = 'ecom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR /'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # addintional context processors
                'ecomapp.context_processors.categories',
                'basketapp.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecom.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'awakzfip_awake',
        'USER': 'awakzfip_kal',
        'PASSWORD': 'jamir1.022',  # the password you set in cPanel
        'HOST': 'localhost',              # or the full domain if remote
        'PORT': '3306',
    }
}





DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



# STATIC_URL = 'static/'
# STATICFILES_DIRS = [ BASE_DIR / 'static' ]

# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
STATICFILES_DIRS = [ BASE_DIR / 'static' ]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


######## These tell django about the custom user modal we created ########
AUTH_USER_MODEL = 'useraccounts.UserBase'




DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'





# SECURE_SSL_REDIRECT = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True


# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# consumer_key: TDpigBOOhs+zAl8cwH2Fl82jJGyD8xev
# consumer_secret: 1KpqkfsMaihIcOlhnBo/gBZ5smw=



# PESAPAL_CONSUMER_KEY = '0IvCo5VfHebocBulSLEeLlQlU13f1Y+0'
# PESAPAL_CONSUMER_SECRET = '+EDtZ0OSUa56evNPYaQKFoOFtdI='

PESAPAL_CONSUMER_KEY = 'TDpigBOOhs+zAl8cwH2Fl82jJGyD8xev'
PESAPAL_CONSUMER_SECRET = '1KpqkfsMaihIcOlhnBo/gBZ5smw='
PESAPAL_ENVIRONMENT = 'sandbox'  # Change to 'live' for production and 'sandbox' for test
PESAPAL_NOTIFICATION_ID = ''  # Optional: Get from PesaPal IPN settings
DEFAULT_CURRENCY = 'USD'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'awakeningsaints.org'              # ✅ from "Outgoing Server"
EMAIL_PORT = 465                                # ✅ from "SMTP Port"
EMAIL_USE_SSL = True                            # ✅ because port 465 = SSL
EMAIL_HOST_USER = 'info@awakeningsaints.org'    # ✅ or use 'noreply@...' if created
EMAIL_HOST_PASSWORD = 'Christjesus1@!'    # 🔑 this is the password for the mailbox
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER







