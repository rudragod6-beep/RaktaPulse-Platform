import os
import time
from .models import Message

def unread_messages(request):
    if request.user.is_authenticated:
        return {
            'unread_messages_count': Message.objects.filter(receiver=request.user, is_read=False).count()
        }
    return {'unread_messages_count': 0}

def project_context(request):
    """
    Adds project-specific environment variables to the template context globally.
    """
    return {
        "project_description": os.getenv("PROJECT_DESCRIPTION", ""),
        "project_image_url": os.getenv("PROJECT_IMAGE_URL", ""),
        # Used for cache-busting static assets
        "deployment_timestamp": int(time.time()),
    }
