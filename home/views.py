from django.shortcuts import render, redirect
from home.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from instamojo_wrapper import Instamojo
from django.conf import settings

api = Instamojo(api_key=settings.API_KEY,
                auth_token=settings.AUTH_TOKEN, endpoint="https://test.instamojo.com/api/1.1/")


# Create your views here.

def home(request):
    pizzas = Pizza.objects.all()
    context = {'pizzas': pizzas}
    return render(request, 'home.html', context)


def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            print('User not found..')
            return redirect('/login')
        user = authenticate(username=username, password=password)
        if user is None:
            print('wrong password')
            return redirect('/login')
        login(request, user)
        print('Loggin SUccessfully')
        return redirect('/')
    return render(request, 'login.html')


def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            if User.objects.filter(username=username).first():
                print('Username is allready taken')
                return redirect('/login/')

            user_obj = User.objects.create_user(username=username)
            user_obj.set_password(password)
            user = user_obj.save()
            print('Account Created successfully')
        except Exception as e:
            print(e)
    return render(request, 'register.html')


def add_cart(request, pizza_uid):
    user = request.user
    pizza_obj = Pizza.objects.get(uid=pizza_uid)
    cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)
    cart_items = CartItems.objects.create(
        cart=cart,
        pizza=pizza_obj
    )
    return redirect('/')


def cart(request):
    cart = Cart.objects.get(is_paid=False, user=request.user)
    context = {'carts': cart}
    response = api.payment_request_create(
        amount=cart.get_cart_total(),
        purpose="Order",
        buyer_name=request.user.username,
        email="m.kale0304@gmail.com",
        redirect_url="http://127.0.0.1:8000/success"
    )
    print(response)
    return render(request, 'cart.html', context)


def remove_cart_items(request, cart_item_uid):
    try:
        CartItems.objects.get(uid=cart_item_uid).delete()
        return redirect('/cart/')
    except Exception as e:
        print(e)


def orders(request):
    orders = Cart.objects.filter(is_paid=True, user=request.user)
    context = {'orders': orders}
    return render(request, 'orders.html', context)


def process_payment(request):
    return render(request, 'payment.html')
