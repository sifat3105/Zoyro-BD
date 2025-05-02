from django.db import models
from django.contrib.auth.models import User

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField()
    valid_from = models.DateField()
    valid_until = models.DateField()
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    minimum_spend = models.DecimalField(max_digits=10, decimal_places=2, default=500)  

    def __str__(self):
        return self.code

    def is_applicable(self, request):
        cart = getattr(request.user, 'cart', None)
        if cart: 
            total_spent = cart.get_total_offer_price()
        else:
            total_spent = 0 
        if total_spent >= self.minimum_spend:
            return True
        else:
            return False