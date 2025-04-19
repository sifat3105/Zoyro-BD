from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from discounts.models import Coupon
from django.db.models import Sum
from decimal import Decimal


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_total_price(self):
        item_total = sum(item.get_total_price() for item in self.items.all())
        return item_total
    
    def get_total_offer_price(self):
        item_total = sum(item.get_total_offer_price() for item in self.items.all())
        return item_total

    def get_discount(self):
        if self.coupon:
            discount = Decimal(self.get_total_price()) * Decimal(self.coupon.discount_percentage) / 100
            return min(discount, self.coupon.maximum_discount)
        return Decimal('0.00')

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()

    def get_total_item_count(self):
        return self.items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    
    def get_total_item_count(self):
        return self.items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.cart.user.username}'s Cart Item: {self.product.title} x {self.quantity}"

    def get_total_price(self):
        return self.product.price * self.quantity
    
    def get_total_offer_price(self):
        return self.product.offer_price * self.quantity
