from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
import random



class Order(models.Model):
    """Model representing a customer order."""
    
    # Order status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),

    ]
    
    # Payment method choices
    PAYMENT_CHOICES = [
        ('sslcommerz', 'SSLCommerz'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name='orders')
    order_number = models.CharField(max_length=32, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    payment_method = models.CharField(max_length=20,choices=PAYMENT_CHOICES,default='cash_on_delivery')
    payment_status = models.BooleanField(default=False)
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True, null=True)
    shipping_method = models.CharField(max_length=100, blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    tax_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    discount_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    total_amount = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(Decimal('0.00'))])
    notes = models.TextField(blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    number = models.CharField(max_length=15, blank=True, null=True)
    
    class Meta:
        ordering = ['-order_date']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def save(self, *args, **kwargs):
        if not self.estimated_delivery_date and not self.pk:  # Only set on creation
            # Calculate 3-5 days from now (random or fixed)
            delivery_days = random.randint(3, 5)  # Random between 3-5 days
            # delivery_days = 3  # Fixed 3 days (if preferred)
            self.estimated_delivery_date = timezone.now().date() + timezone.timedelta(days=delivery_days)
        super().save(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        # Generate order number if it doesn't exist
        if not self.order_number:
            # Get the last order and increment the number
            last_order = Order.objects.order_by('-id').first()
            if last_order and last_order.order_number:
                try:
                    # Extract number from "ORD-1000" format
                    last_number = int(last_order.order_number.split('-')[1])
                    self.order_number = f"ORD-{last_number + 1}"
                except (IndexError, ValueError):
                    # Fallback if format is wrong
                    self.order_number = f"ORD-{last_order.id + 1000}"
            else:
                self.order_number = "ORD-1000"
        
        # Set estimated delivery date if it's a new order and not set
        if not self.estimated_delivery_date and not self.pk:
            delivery_days = random.randint(3, 5)
            self.estimated_delivery_date = timezone.now().date() + timezone.timedelta(days=delivery_days)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number}"
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.customer}"
    
    
    
    
    @property
    def items_count(self):
        """Return the total count of items in the order."""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0


class OrderItem(models.Model):
    """Model representing an item within an order."""
    
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(Decimal('0.00'))])
    size = models.CharField(max_length=5, blank=True, null=True)
    discount = models.DecimalField(max_digits=5,decimal_places=2,default=0.00,validators=[MinValueValidator(Decimal('0.00'))])
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.quantity} x {self.product} (Order #{self.order.order_number})"
    
    @property
    def total_price(self):
        """Calculate the total price for this order item."""
        return (self.unit_price - self.discount) * self.quantity