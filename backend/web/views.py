from django.views.generic import TemplateView

class Home(TemplateView):
    template_name = "core/index.html"

class Privacy(TemplateView):
    template_name = "core/privacy.html"

class Terms(TemplateView):
    template_name = "core/terms.html"

class Contact(TemplateView):
    template_name = "core/contact.html"