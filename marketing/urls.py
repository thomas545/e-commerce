"""products App URL Configuration"""
from django.urls import path
from .views import MarketingPreferenceUpdateView, MailchimpWebhookView



app_name = 'marketing'




urlpatterns = [

    path('settings/email/', MarketingPreferenceUpdateView.as_view(), name='MarketingUpdateView'),
    path('mailchimp/webhooks', MailchimpWebhookView.as_view(), name='webhooks'),

]
