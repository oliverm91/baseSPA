from django.conf import settings

def global_settings(request):
    """
    Exposes specific settings variables to all templates context globally.
    """
    return {
        'APP_NAME': getattr(settings, 'APP_NAME', 'BaseSPA'),
    }
