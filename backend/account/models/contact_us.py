from django.db import models

class ContactUs(models.Model):
    class SubjectChoices(models.TextChoices):
        TECHNICAL_SUPPORT = "technical_support", "Technical Support"
        PRIVACY_DATA_REQUEST = "privacy_data_request", "Privacy / Data Request"
        FEATURE_REQUEST = "feature_request", "Feature Request"
        BUG_REPORT = "bug_report", "Bug Report"
        BUSINESS_PARTNERSHIP = "business_partnership", "Business / Partnership"
        OTHER = "other", "Other"

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=50, choices=SubjectChoices.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"
        ordering = ['-created_at']
