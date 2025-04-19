from django.contrib import admin
from django.utils.html import format_html
from .models import Category, SubCategory, Product, ProductImage, ApparelSize

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_preview', 'image', 'alt_text')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Preview'

class ApparelSizeInline(admin.TabularInline):
    model = ApparelSize
    extra = 1
    fields = ('size', 'quantity')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'product_count')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail',
        'title',
        'category',
        'subcategory',
        'price',
        'offer_price',
        'discount_display',
        'availability_status',
        'is_active',
        'click_count',
        'total_orders',
    )
    list_filter = (
        'category',
        'subcategory',
        'availability',
        'top_sell',
        'is_active',
    )
    search_fields = (
        'title',
        'product_code',
        'sku',
        'category__name',
        'subcategory__name',
    )
    list_editable = (
        'price',
        'offer_price',
        'is_active',
    )
    readonly_fields = (
        'slug',
        'click_count',
        'total_orders',
        'created_at',
        'updated_at',
        'image_preview',
    )
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'slug',
                'product_code',
                'sku',
                'quick_overview',
                'additional_description',
                'category',
                'subcategory',
            )
        }),
        ('Pricing & Inventory', {
            'fields': (
                'price',
                'offer_price',
                'discount',
                'quantity',
                'availability',
            )
        }),
        ('Marketing', {
            'fields': (
                'top_sell',
                'review',
                'is_active',
            )
        }),
        ('Media', {
            'fields': (
                'default_image',
                'image_preview',
            )
        }),
        ('Statistics', {
            'fields': (
                'click_count',
                'total_orders',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [ProductImageInline, ApparelSizeInline]
    actions = ['activate_products', 'deactivate_products', 'mark_as_top_sell']
    list_per_page = 25
    save_on_top = True
    
    def image_thumbnail(self, obj):
        if obj.default_image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.default_image.url)
        return "-"
    image_thumbnail.short_description = 'Image'
    
    def image_preview(self, obj):
        if obj.default_image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.default_image.url)
        return "No image uploaded"
    image_preview.short_description = 'Preview'
    
    def discount_display(self, obj):
        return f"{obj.discount}%" if obj.discount else "-"
    discount_display.short_description = 'Discount'
    discount_display.admin_order_field = 'discount'
    
    def availability_status(self, obj):
        color_map = {
            'in_stock': 'green',
            'out_of_stock': 'red',
            'pre_order': 'orange'
        }
        color = color_map.get(obj.availability, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_availability_display()
        )
    availability_status.short_description = 'Availability'
    availability_status.admin_order_field = 'availability'
    
    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} products activated.')
    activate_products.short_description = 'Activate selected products'
    
    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} products deactivated.')
    deactivate_products.short_description = 'Deactivate selected products'
    
    def mark_as_top_sell(self, request, queryset):
        updated = queryset.update(top_sell=True)
        self.message_user(request, f'{updated} products marked as top sellers.')
    mark_as_top_sell.short_description = 'Mark as Top Sell'

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'alt_text')
    search_fields = ('product__title', 'alt_text')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Preview'

@admin.register(ApparelSize)
class ApparelSizeAdmin(admin.ModelAdmin):
    list_display = ('get_product', 'size', 'quantity')
    list_filter = ('size',)
    search_fields = ('product__title', 'size')
    
    def get_product(self, obj):
        return obj.product.title
    get_product.short_description = 'Product'
    get_product.admin_order_field = 'product__title'