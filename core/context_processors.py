# core/context_processors.py
def global_context(request):
    return {
        'site_name': 'LinkHub',
        'site_tagline': 'All Important Links in One Place',
    }