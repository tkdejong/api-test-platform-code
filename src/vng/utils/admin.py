from django.contrib.staticfiles.templatetags.staticfiles import static


class AdminStaticFile():

    class Media:
        css = {
            'all': ('css/admin.css',)
        }
