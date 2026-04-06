from django.views.generic import TemplateView

class Home(TemplateView):
    template_name = "web/index.html"

class Privacy(TemplateView):
    template_name = "web/privacy.html"

class Terms(TemplateView):
    template_name = "web/terms.html"

class Contact(TemplateView):
    template_name = "web/contact.html"