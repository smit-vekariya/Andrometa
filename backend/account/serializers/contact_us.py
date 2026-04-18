from rest_framework import serializers
from account.models import ContactUs

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['first_name', 'last_name', 'email', 'subject', 'message']
