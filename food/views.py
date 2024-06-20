from .models import Product, Order, OrderItem
from .forms import SignUpForm
from .signals import order_completed
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group

def is_staff(user):
    return user.groups.filter(name='Staff').exists()

def is_customer(user):
    return user.groups.filter(name='Customers').exists()
# Create your views here.

def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return redirect('food:login')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            customers_group = Group.objects.get(name='Customers')
            # Add the user to the group
            user.groups.add(customers_group)
            login(request, user)  # Log the user in after successful sign-up
            return redirect('food:product_list')  # Redirect to home or any other page
    else:
        form = SignUpForm()
    return render(request, 'food/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"You are now logged in as {username}.")
                print('1')
                if user.groups.filter(name='Customers').exists():
                    print('2')
                    return redirect('food:product_list')
                elif user.groups.filter(name='Staff').exists():
                    return redirect('food:deliver')  # Replace with your desired redirect
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "food/login.html", {"form": form})

@login_required
@user_passes_test(is_customer)
def product_list(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'food/product_list.html', context)
    

@login_required
@user_passes_test(is_customer)
def add_to_cart(request, product_id):
    order, created = Order.objects.get_or_create(user=request.user, completed=False)
    product = get_object_or_404(Product, id=product_id)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    order_item.quantity += 1
    order_item.save()

    return redirect('food:product_list')

@login_required
@user_passes_test(is_customer)
def cart_view(request):
    order = Order.objects.filter(user=request.user, completed=False).first()
    numbers = range(1, 101)
    selected_number = None

    if request.method == "POST":
        selected_number = int(request.POST.get("numbers"))
        item_id = request.POST.get('item_id')
        order_item = OrderItem.objects.get(pk=item_id)
        order_item.quantity = selected_number
        order_item.save()

    context = {
        'numbers': numbers,
        'selected_number': selected_number,
        'order': order
    }

    return render(request, 'food/cart_detail.html', context)

def delete_order_item(request, item_id):
    try:
        order_item = OrderItem.objects.get(pk=item_id, order__user=request.user, order__completed=False)
        order_item.delete()
    except OrderItem.DoesNotExist:
        pass

    return redirect('food:cart_view')

@login_required
@user_passes_test(is_customer)
def checkout(request):
    order = Order.objects.get(user=request.user, completed=False)
    total = order.get_total()
    print(total)  
    order.checkout = True
    order.save()

    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    order_data = {
        'id': order.id,
        'created_at': order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        'total': str(order.get_total),
        'user_id': order.user.id,
    }

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'orders',
        {
            'type': 'order.message',
            'order': order_data
        }
    )
    return redirect('food:preparing')

@login_required
@user_passes_test(is_staff)
def deliver(request):
    orders = Order.objects.filter(completed=False, checkout=True)
    if request.method =='POST':
        order_id = request.POST.get('order_id')
        order_user = request.POST.get('order_user')
        print(order_id) 
        print(order_user)
        order = Order.objects.get(pk=order_id)
        order.completed = True
        order.save()
        order_completed.send(sender=Order, user=order_user, instance=order, completed=order.completed)
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        event_data = {
            'user_id': order_user,
            'redirect_url': '/served',
        }
        async_to_sync(channel_layer.group_send)(
            f'user_{order_user}',
            {
                'type': 'check_redirect',
                'event': event_data,
            }
        )
    return render(request, 'food/deliver.html' , {'orders':orders})

def served(request):
    return render(request, 'food/served.html')

def preparing(request):
    user_id = request.user.id
    return render(request, 'food/preparing.html',{'user_id':user_id})
