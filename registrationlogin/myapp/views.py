from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from myapp.models import ProductTable,CartTable
from django.db.models import Q
from django.contrib import messages
from myapp.models import CustomerDeatils
import razorpay

# Create your views here.
def register_user(request):
    data={}
    if request.method=="POST":
        uname=request.POST["username"]
        upass=request.POST["password"]
        uconf_pass=request.POST["password2"]
        if (uname=='' or upass =='' or uconf_pass ==''):
            data['error_msg']='Fields cant be empty'
            return render(request,'myapp/register.html',context=data)
        elif(upass!=uconf_pass):
            data['error_msg']='Password and confirm password not matches'
            return render(request,'myapp/register.html',context=data)
        elif(User.objects.filter(username=uname).exists()):
            data['error_msg']= uname +' allready exits'
            return render(request,'myapp/register.html',context=data)
        else:
            user=User.objects.create(username=uname)
        user.set_password(upass)
        user.save()
        customer=CustomerDeatils.objects.create(uid=user)
        customer.save()
        return HttpResponse("Registartion done")
    return render(request,'myapp/register.html')

def login_user(request):
    data={}
    if request.method=="POST":
        uname=request.POST["username"]
        upass=request.POST["password"]
        if (uname=='' or upass ==''):
            data['error_msg']='Fields cant be empty'
            return render(request,'myapp/login.html',context=data)
        elif(not User.objects.filter(username=uname).exists()):
            data['error_msg']= uname + ' user is not registerd'
            return render(request,'myapp/login.html',context=data)
        else:
            user=authenticate(username=uname,password=upass)
            if user is not None:
                login(request,user)
                return redirect("/myapp/home")
            else:
                data['error_msg']='wrong password'
                return render(request,'myapp/login.html',context=data)
    return render(request,'myapp/login.html')

def home(request):
    mydata={}
    fetched_products=ProductTable.objects.filter(is_active=True)
    mydata['products']=fetched_products
    user_id = request.user.id
    id_specific_cart_items = CartTable.objects.filter(uid=user_id)
    count = id_specific_cart_items.count()
    mydata['cart_count'] = count
    return render(request,'myapp/home.html',context=mydata)


def user_logout(request):
    logout(request)
    return render(request,'myapp/home.html',{'user_data':'User'})

def home_navbar(request):
    data={}
    user_authenticated=request.user.is_authenticated
    if(user_authenticated):
        user_id = request.user.id
        user=User.objects.get(id=user_id)
        data['user_data']= user.username
        return render(request,'myapp/home.html',context=data)
    else:
        data['user_data'] = 'User'
    return render(request,'myapp/home.html',{'user':user})
    
def filter_by_category(request,category_value):
    mydata={}
    q1 = Q(is_active=True)
    q2 = Q(category=category_value)
    filtered_products = ProductTable.objects.filter(q1 & q2)
    mydata['products']=filtered_products
    return render(request,'myapp/home.html',context= mydata)

def sort_by_price(request,sort_value):
    data={}
    if sort_value=='asc':
        price = 'price'
    else:
        price= '-price'
    sorted_products=ProductTable.objects.filter(is_active=True).order_by(price)
    data['products']=sorted_products
    return render(request,'myapp/home.html',context= data)

def sort_by_rating(request,rating_value):
    data={}
    q1= Q(is_active=True)
    q2= Q(rating__gt=rating_value)
    filtered_products=ProductTable.objects.filter(q1 & q2)
    data['products']=filtered_products
    return render(request,'myapp/home.html',context=data)

def filter_by_price_range(request):
    data={}
    min = request.GET['min']
    max = request.GET['max']
    q1 = Q(price__gte=min)
    q2 = Q(price__lte=max)
    q3 = Q(is_active=True)
    filtered_products=ProductTable.objects.filter(q1 & q2 & q3 )
    data['products']=filtered_products
    return render(request,'myapp/home.html',context=data)

def product_detail(request,pid):
    product=ProductTable.objects.get(id=pid)
    return render(request,'myapp/product_detail.html',{'product':product})

def add_to_cart(request,pid):
    if request.user.is_authenticated:
        uid = request.user.id
        print("user id = ",uid)
        print("product id =",pid)
        user=User.objects.get(id=uid)
        product=ProductTable.objects.get(id=pid)

        q1 = Q(uid = uid)
        q2 = Q(pid = pid)
        available_products=CartTable.objects.filter(q1 & q2)
        print()
        if(available_products.count()>0):
            messages.error(request,'Product is already added to cart.')       
            return redirect('/myapp/home')
        else:
            cart=CartTable.objects.create(pid=product,uid=user)
            cart.save()
            messages.success(request,"")
        cart=CartTable.objects.create(pid=product,uid=user)
        cart.save()
        return redirect("/myapp/home")
    else:
        return redirect("/user/login")
    

def view_cart(request):
    if request.user.is_authenticated:
        data ={}
        user_id =request.user.id
        user=User.objects.get(id=user_id)
        id_specific_cartitems=CartTable.objects.filter(uid=user_id)
        data['products']=id_specific_cartitems
        # data['user']=user
        count=id_specific_cartitems.count()
        # data['cart_count']=count
        total_price = 0
        total_quantity = 0
        for item in id_specific_cartitems:
            total_price=total_price+(item.pid.price*item.quantity)
            total_quantity+=item.quantity
        data['total_price']=total_price  
        data['cart_count']=total_quantity
        return render(request,'myapp/cart.html',context=data) 

def remove_item(request,cartid):
    cart=CartTable.objects.filter(id=cartid)
    cart.delete()
    return redirect('/myapp/view_cart')

def update_quantity(request,flag,cartid):
    cart=CartTable.objects.filter(id=cartid)
    actual_quantity = cart[0].quantity
    if(flag=="1"):
        cart.update(quantity = actual_quantity)
        pass
    else:
        if(actual_quantity):
            cart.update(quantity = actual_quantity-1)
            pass
    return redirect('/myapp/view_cart')

import calendar
import time 
from .models import OrderTable
def place_order(request):
    current_GHT = time.gmtime()
    time_stamp = calendar.timegm(current_GHT)
    user_id = request.user.id
    oid=str(user_id)+"-"+str(time_stamp)
    cart=CartTable.objects.filter(uid=user_id)
    for data in cart:
        order=OrderTable.objects.create(order_id=oid,quantity=data.quantity,pid=data.pid,uid=data.uid)
        order.save()
    return HttpResponse("order placed")


def place_order(request):
        data ={}
        user_id =request.user.id
        user=User.objects.get(id=user_id)
        id_specific_cartitems=CartTable.objects.filter(uid=user_id)
        customer = CustomerDeatils.objects.get(uid = user_id)
        data['customer']=customer
        data['products']=id_specific_cartitems
        data['user']=user
        total_price = 0
        total_quantity = 0
        for item in id_specific_cartitems:
            total_price=(total_price+item.pid.price)*(item.quantity)
            total_quantity+=item.quantity
        data['total_price']=total_price  
        data['cart_count']=total_quantity
        return render(request,'myapp/order.html',context=data)

def edit_profile(request):
    data={}
    user_id = request.user.id
    customer_query_set = CustomerDeatils.objects.filter(uid = user_id)
    customer = customer_query_set[0]
    data['customer'] = customer
    if request.method=='POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        email = request.POST['email']
        address_type = request.POST['address_type']
        full_address = request.POST['full_address']
        pincode = request.POST['pincode']
        customer_query_set.update(first_name = first_name,last_name = last_name,phone = phone,email = email,address_type = address_type,full_address = full_address,pincode = pincode)
        return redirect('/myapp/home')
    return render(request,'user/edit_profile.html',context=data)

def make_payment(request):
    data={}
    user_id=request.user.id
    id_specific_cartitems=CartTable.objects.filter(uid=user_id)
    total_price = 0
    for item in id_specific_cartitems:
        total_price=(total_price+item.pid.price)*(item.quantity)

    client = razorpay.Client(auth=("rzp_test_gI14MhzZKkZDum", "cuQC7MctBNDB1Oh2oarYujnv"))
    # data = { "amount": 500, "currency": "INR", "receipt": "order_rcptid_11" }
    data['amount']=total_price*100
    data['currency']="INR"
    data['recepit']="order_rcptid_11"
    payment = client.order.create(data=data)
    print(payment)
    return HttpResponse("payment done")

