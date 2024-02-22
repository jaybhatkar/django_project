from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ProductTable(models.Model):
    CATEGORIES= ((1,"Mobile"),(2,"Clothes"),(3,"Shoes"))
    name=models.CharField(max_length=100)
    price=models.FloatField()
    details=models.CharField(max_length=100)
    category=models.IntegerField(choices=CATEGORIES)
    is_active=models.BooleanField()
    rating= models.IntegerField()
    image=models.ImageField(upload_to='image')
    
    def _str_(self):
        return self.name + " added to table"
    
class CartTable(models.Model):
    uid = models.ForeignKey(User,on_delete = models.CASCADE,db_column="uid")
    pid = models.ForeignKey(ProductTable,on_delete =models.CASCADE,db_column="pid")
    quantity = models.IntegerField(default=1)

class OrderTable(models.Model):
    order_id = models.CharField(max_length=50)
    uid = models.ForeignKey(User, on_delete = models.CASCADE, db_column="uid")
    pid = models.ForeignKey(ProductTable, on_delete = models.CASCADE, db_column="pid")
    quantity = models.IntegerField()

class CustomerDeatils(models.Model):
    ADDRESS_TYPE = (('home','Home'),('office','Office'),('other','Other'))
    uid= models.ForeignKey(User,on_delete = models.CASCADE, db_column="uid")
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=20)
    address_type = models.CharField(max_length=10,choices=ADDRESS_TYPE)
    full_address= models.CharField(max_length=200)
    pincode =models.CharField(max_length=10)