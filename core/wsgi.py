import os
from django.core.wsgi import get_wsgi_application
# 1. Import load_dotenv
from dotenv import load_dotenv 

# 2. Load the .env file
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.production')

application = get_wsgi_application()