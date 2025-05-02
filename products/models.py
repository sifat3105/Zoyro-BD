from django.db import models

# Create your models here.
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('search:search_redirect') + f'?q={self.name}'

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('category', 'name')
        verbose_name_plural = "Subcategories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.category.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} → {self.name}"
    
    def get_absolute_url(self):
        return reverse('search:search_redirect') + f'?q={self.name}'

class Brand(models.Model):
    name = models.CharField(max_length=100, default="ZOYRO")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name



AVAILABILITY_CHOICES = [
    ('in_stock', 'In Stock'),
    ('out_of_stock', 'Out of Stock'),
    ('pre_order', 'Pre-Order'),
]

class Product(models.Model):
    title = models.CharField(max_length=255)
    product_code = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount = models.PositiveIntegerField(help_text="Discount in percentage", blank=True, null=True)
    quantity = models.PositiveIntegerField()
    quick_overview = models.TextField()
    additional_description = models.TextField(blank=True, null=True)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='in_stock')
    top_sell = models.BooleanField(default=False)
    review = models.TextField(blank=True, null=True)
    default_image = models.ImageField(upload_to='products/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    total_orders = models.PositiveIntegerField(default=0, help_text="Total number of orders for this product")
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE, blank=True, null=True, default=1)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Auto-generate slug if not set
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-calculate discount
        if self.offer_price and self.price:
            self.discount = int(((self.price - self.offer_price) / self.price) * 100)

        # Auto-set category based on subcategory
        if self.subcategory and not self.category:
            self.category = self.subcategory.category

        if self.quantity == 0:
            self.availability = 'Out of Stock'
        elif self.availability == 'out_of_stock' and self.quantity > 0:
            # Optional: Set back to 'in_stock' if quantity becomes positive
            self.availability = 'In Stock'
        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('products:details', args=[self.slug])



    def get_quantity_for_size(self, size):
            try:
                return self.apparel_sizes.get(size=size).quantity
            except ApparelSize.DoesNotExist:
                return 0

    
    def __str__(self):
        return self.title

    
class ApparelSize(models.Model):
    APPAREL_SIZES = [
    ('XS', 'Extra Small'),
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
    ('XL', 'Extra Large'),
    ('XXL', 'Double Extra Large'),
]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='apparel_sizes')
    size = models.CharField(max_length=5, choices=APPAREL_SIZES)
    quantity = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.size
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/extra_images/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.product.title}"
