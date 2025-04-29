from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from .models import DeliverySettings, DeliveryAddress



@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    # Basic configuration
    fields = ('maxbuy',)  # Only show the maxbuy field
    list_display = ('current_maxbuy',)  # Simple list view
    
    # Remove all unnecessary actions and options
    actions = []
    list_display_links = ()
    list_editable = ()
    
    # Singleton enforcement
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    # Redirect list view directly to edit view
    def changelist_view(self, request, extra_context=None):
        obj = DeliverySettings.get()
        return HttpResponseRedirect(
            reverse('admin:%s_%s_change' % (
                self.model._meta.app_label,
                self.model._meta.model_name
            ), args=(obj.pk,))
        )
    
    # Custom display for the list view (though it redirects)
    def current_maxbuy(self, obj):
        return format_html(
            '<span style="font-weight:bold;">Max Buy:</span> ${:,}'.format(obj.maxbuy)
        )
    current_maxbuy.short_description = 'Current Setting'
    
    # Simplify the change form view
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_delete'] = False
        return super().changeform_view(
            request, object_id, form_url, extra_context=extra_context
        )
    



@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'district', 'upazila', 'is_default')
    list_filter = ('division', 'district', 'address_type')
    search_fields = ('full_name', 'phone_number', 'complete_address')