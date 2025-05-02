from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'valid_from', 'valid_until', 
                   'maximum_discount', 'minimum_spend', 'is_active')
    list_filter = ('valid_from', 'valid_until')
    search_fields = ('code',)
    date_hierarchy = 'valid_from'
    ordering = ('-valid_from',)
    
    fieldsets = (
        (None, {
            'fields': ('code', 'discount_percentage')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until'),
            'classes': ('collapse',)
        }),
        ('Conditions', {
            'fields': ('maximum_discount', 'minimum_spend'),
            'description': 'Set the conditions for applying this coupon'
        }),
    )
    
    def is_active(self, obj):
        from django.utils.timezone import now
        return obj.valid_from <= now().date() <= obj.valid_until
    is_active.boolean = True
    is_active.short_description = 'Currently Active'