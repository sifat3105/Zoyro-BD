from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('get_total_price',)
    fields = ('product', 'quantity', 'get_total_price')
    can_delete = True


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'get_total_item_count', 'get_total_price', 'get_discount', 'get_total_price_after_discount')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'get_total_price', 'get_discount', 'get_total_item_count', 'get_total_price_after_discount')
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'get_total_price')
    search_fields = ('cart__user__username', 'product__title')
    list_filter = ('product',)

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = "Total Price"
