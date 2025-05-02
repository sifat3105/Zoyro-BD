from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'unit_price', 'discount', 'total_price')
    fields = ('product', 'quantity', 'unit_price', 'discount', 'total_price')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'customer_email',
        'order_date_short',
        'status_badge',
        'payment_status_badge',
        'total_amount_formatted',
        'items_count',
    )
    list_filter = (
        'status',
        'payment_status',
        'order_date',
        'payment_method',
    )
    search_fields = (
        'order_number',
        'customer__email',
        'customer__first_name',
        'customer__last_name',
        'shipping_address',
        'billing_address',
    )
    readonly_fields = (
        'order_number',
        'order_date',
        'customer_info',
        'total_amount',
        'items_count',
        'payment_status',
    )
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number',
                'order_date',
                'status',
                'customer_info',
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method',
                'payment_status',
                'total_amount',
                'tax_amount',
                'discount_amount',
            )
        }),
        ('Shipping Information', {
            'fields': (
                'shipping_address',
                'billing_address',
                'shipping_method',
                'shipping_cost',
                'tracking_number',
                'estimated_delivery_date',
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes',
                'items_count',
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = (OrderItemInline,)
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    date_hierarchy = 'order_date'
    list_per_page = 25

    def customer_email(self, obj):
        return obj.customer.email if obj.customer else 'Guest'
    customer_email.short_description = 'Customer Email'
    customer_email.admin_order_field = 'customer__email'

    def order_date_short(self, obj):
        return obj.order_date.strftime('%Y-%m-%d %H:%M')
    order_date_short.short_description = 'Order Date'
    order_date_short.admin_order_field = 'order_date'

    def status_badge(self, obj):
        status_colors = {
            'pending': 'orange',
            'processing': 'blue',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red',
            'refunded': 'gray',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            status_colors.get(obj.status, 'gray'),
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def payment_status_badge(self, obj):
        color = 'green' if obj.payment_status else 'red'
        text = 'PAID' if obj.payment_status else 'UNPAID'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, text
        )
    payment_status_badge.short_description = 'Payment'
    payment_status_badge.admin_order_field = 'payment_status'

    def total_amount_formatted(self, obj):
        return f"${obj.total_amount:.2f}"
    total_amount_formatted.short_description = 'Total'
    total_amount_formatted.admin_order_field = 'total_amount'

    def customer_info(self, obj):
        if obj.customer:
            return format_html(
                '{}<br>{}<br>{}',
                obj.customer.get_full_name(),
                obj.customer.email,
                obj.customer.phone_number if hasattr(obj.customer, 'phone_number') else ''
            )
        return 'Guest Order'
    customer_info.short_description = 'Customer Details'

    def mark_as_processing(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = 'Mark selected as Processing'

    def mark_as_shipped(self, request, queryset):
        updated = queryset.filter(status='processing').update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = 'Mark selected as Shipped'

    def mark_as_delivered(self, request, queryset):
        updated = queryset.filter(status='shipped').update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = 'Mark selected as Delivered'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'product_title',
        'quantity',
        'unit_price_formatted',
        'discount_formatted',
        'total_price_formatted',
    )
    list_filter = ('order__status',)
    search_fields = (
        'order__order_number',
        'product__title',
    )
    readonly_fields = (
        'order',
        'product',
        'quantity',
        'unit_price',
        'discount',
    )

    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Order Number'
    order_number.admin_order_field = 'order__order_number'

    def product_title(self, obj):
        return obj.product.title if obj.product else '[Deleted Product]'
    product_title.short_description = 'Product'
    product_title.admin_order_field = 'product__title'

    def unit_price_formatted(self, obj):
        return f"${obj.unit_price:.2f}"
    unit_price_formatted.short_description = 'Unit Price'
    unit_price_formatted.admin_order_field = 'unit_price'

    def discount_formatted(self, obj):
        return f"${obj.discount:.2f}"
    discount_formatted.short_description = 'Discount'
    discount_formatted.admin_order_field = 'discount'

    def total_price_formatted(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_formatted.short_description = 'Total'