from django.shortcuts import *
from .basket import cartbasket
from django.http import JsonResponse
from ecomapp.models import *
import json, hashlib, hmac, os
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
import mimetypes
from django.http import HttpResponse, Http404
from django.utils.timezone import now, timedelta
from django.core.signing import TimestampSigner
from django.urls import reverse
from django.core.signing import BadSignature, SignatureExpired
from django.core.signing import TimestampSigner
from django.http import HttpResponseForbidden
from ecomapp.models import *
import requests
from django.conf import settings
import urllib.request
import urllib.parse
import urllib.error
import uuid
from decimal import Decimal

signer = TimestampSigner()


# Show cart page
@login_required
def basket_summary(request):
    cart = cartbasket(request)
    return render(request, 'cart/basketapp/cart.html', {'cart': cart})

# Add product to cart
def cart_add(request):
    basket = cartbasket(request)
    if request.POST.get('action') == 'post':
        try:
            product_id = int(request.POST.get('product_id'))
            product_qty = int(request.POST.get('productqty'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid product ID or quantity'}, status=400)

        product = get_object_or_404(Product, id=product_id)
        basket.add(product=product, qty=product_qty)

        total_qty = len(basket)
        return JsonResponse({
            'message': 'Product added',
            'product_id': product_id,
            'qty': product_qty,
            'cart_count': total_qty
        })
    return JsonResponse({'error': 'Invalid action'}, status=400)

# Update product quantity in cart
@require_POST
def cart_update(request):
    basket = cartbasket(request)
    
    if request.POST.get('action') == 'post':
        try:
            product_id = int(request.POST.get('productid'))
            product_qty = int(request.POST.get('productqty'))
            if product_qty < 1:
                product_qty = 1
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid input'}, status=400)

        basket.update(product=product_id, qty=product_qty)

        return JsonResponse({
            'cart_count': len(basket),
            'subtotal': basket.get_total_price()
        })

    return JsonResponse({'error': 'Invalid action'}, status=400)

# Remove product from cart
def cart_delete(request):
    cart = cartbasket(request)
    if request.POST.get('action') == 'post':
        try:
            product_id = int(request.POST.get('productid'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid product ID'}, status=400)

        cart.delete(product=product_id)

        return JsonResponse({
            'subtotal': cart.get_total_price(),
            'cart_count': len(cart)
        })
    return JsonResponse({'error': 'Invalid action'}, status=400)

# Checkout view
@login_required
def checkout_view(request):
    basket = cartbasket(request)
    cart_items = []

    for item in basket:
        product = item.get('product')
        if not product:
            continue
        cart_items.append({
            'id': product.id,
            'name': product.title,
            'price': float(product.product_price),
            'qty': item['qty']
        })

    cart_json = json.dumps(cart_items)
    return render(request, 'cart/basketapp/checkout.html', {'cart_json': cart_json})

# -----------------------------
# PesaPal Integration Functions for LIVE/PRODUCTION
# -----------------------------

def payment_success(request):
    """Handle legacy payment success redirects - now using PesaPal"""
    # Check for PesaPal parameters first
    order_tracking_id = request.GET.get('OrderTrackingId')
    order_merchant_reference = request.GET.get('OrderMerchantReference')
    
    if order_tracking_id and order_merchant_reference:
        # This is a PesaPal callback, redirect to proper handler
        return redirect(f'{reverse("cart:pesapal_callback")}?OrderTrackingId={order_tracking_id}&OrderMerchantReference={order_merchant_reference}')
    
    # Check for legacy Flutterwave parameter
    tx_ref = request.GET.get("tx_ref")
    if tx_ref:
        try:
            # Try to find PesaPal order with this reference
            order = BookOrder.objects.get(tx_ref=tx_ref)
            
            # Check if order is already paid
            if order.status == 'collected':
                messages.success(request, "Payment successful! Your downloads are ready.")
                return redirect('cart:download_page', order_id=order.id)
            
            # Try to verify with PesaPal
            return redirect('cart:order_status', order_id=order.id)
            
        except BookOrder.DoesNotExist:
            messages.error(request, "Order not found")
    
    # Default fallback
    messages.info(request, "Please check your orders for payment status.")
    return redirect('cart:checkout')

def get_pesapal_token():
    """Get PesaPal access token for sandbox or live based on settings."""
    try:

        env = getattr(settings, 'PESAPAL_ENVIRONMENT', 'sandbox').lower()
        if env == 'live':
            base_url = 'https://pay.pesapal.com/v3'
            print("Getting PesaPal token (LIVE)...")
        else:
            base_url = 'https://cybqa.pesapal.com/pesapalv3'
            print("Getting PesaPal token (SANDBOX)...")

        url = f'{base_url}/api/Auth/RequestToken'
        consumer_key = settings.PESAPAL_CONSUMER_KEY
        consumer_secret = settings.PESAPAL_CONSUMER_SECRET
        payload = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"PesaPal {env.upper()} Auth URL: {url}")
        print(f"PesaPal {env.upper()} Response Status: {response.status_code}")
        print(f"PesaPal {env.upper()} Response: {response.text}")
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                print(f"PesaPal {env.upper()} token obtained successfully")
                return token
            else:
                print(f"No token in {env.upper()} response: {data}")
                return None
        else:
            print(f"PesaPal {env.upper()} auth failed: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error getting PesaPal {env.upper()} token: {e}")
        import traceback
        traceback.print_exc()
        return None


@csrf_exempt
@require_POST
def save_order(request):
    """Save order to database before PesaPal payment"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        full_name = data.get("full_name", "").strip()
        email = data.get("email", "").strip()
        
        # Handle both 'phone' and 'phone_number' for compatibility
        phone = data.get("phone", "").strip()
        if not phone:  # Try phone_number if phone is empty
            phone = data.get("phone_number", "").strip()
        
        # reference = data.get("reference", f"PESAPAL-LIVE-{uuid.uuid4().hex[:12].upper()}")
        

        env = getattr(settings, 'PESAPAL_ENVIRONMENT', 'sandbox').lower()
        prefix = "PESAPAL-LIVE" if env == "live" else "PESAPAL-SBX"
        reference = data.get(
            "reference",
            f"{prefix}-{uuid.uuid4().hex[:12].upper()}"
        )

        
        
        if not full_name:
            return JsonResponse({"status": "error", "message": "Full name is required"}, status=400)
        
        if not email:
            return JsonResponse({"status": "error", "message": "Email is required"}, status=400)
        
        if not phone:
            return JsonResponse({"status": "error", "message": "Phone number is required"}, status=400)
        
        cart_items = data.get("cart", [])
        if not cart_items:
            return JsonResponse({"status": "error", "message": "Cart is empty"}, status=400)
        
        amount = float(data.get("amount", 0))
        if amount <= 0:
            return JsonResponse({"status": "error", "message": "Invalid order amount"}, status=400)
        
        # Get or create user
        user = request.user if request.user.is_authenticated else None
        
        # Get additional fields for PesaPal
        address = data.get("address", "").strip() or "Not specified"
        city = data.get("city", "").strip() or "Kampala"
        country = data.get("country", "").strip() or "Uganda"
        postal_code = data.get("postal_code", "").strip() or "256"
        currency = data.get("currency", "USD")
        
        # Create order
        order = BookOrder.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            country=country,
            tx_ref=reference,
            total=amount,
            user=user,
            status="pending",
            currency=currency,
            payment_status="pending"
        )
        
        # Save order items
        for item in cart_items:
            try:
                product = Product.objects.get(pk=item["id"])
                qty = int(item["qty"])
                
                BookOrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=product.product_price,
                )
            except Product.DoesNotExist:
                continue
        
        # Update subtotal (same as total for now)
        order.subtotal = amount
        order.save(update_fields=['subtotal'])
        
        print(f"Order saved successfully: ID {order.id}, Reference: {reference}")
        
        return JsonResponse({
            "status": "success",
            "order_id": order.id,
            "reference": reference,
            "message": "Order saved successfully"
        })
        
    except Exception as e:
        print(f"Error saving order: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



@csrf_exempt
@require_POST
def initiate_pesapal_payment(request):
    """
    Initiate PesaPal payment for sandbox or live.
    - Uses environment variables for credentials.
    - Automatically handles sandbox/live URLs and IPN inclusion.
    """
    try:
        data = json.loads(request.body)
        order_id = data.get("order_id")
        reference = data.get("reference")

        if not order_id or not reference:
            return JsonResponse({"status": "error", "message": "Order ID and reference are required"}, status=400)

        order = BookOrder.objects.get(id=order_id, tx_ref=reference)

        # Get PesaPal auth token
        token = get_pesapal_token()
        if not token:
            return JsonResponse({
                "status": "error",
                "message": "Failed to authenticate with PesaPal. Check your credentials and account status."
            }, status=500)

        env = getattr(settings, 'PESAPAL_ENVIRONMENT', 'sandbox').lower()

        # Determine base URL for live or sandbox
        if env == 'live':
            base_url = 'https://pay.pesapal.com/v3'
            scheme = 'https'
            host = 'www.awakeningsaints.org'  # live domain
        else:
            base_url = 'https://cybqa.pesapal.com/pesapalv3'
            scheme = request.scheme
            host = request.get_host()  # ngrok or localhost

        url = f'{base_url}/api/Transactions/SubmitOrderRequest'

        # Callback & cancellation URLs
        callback_url = f"{scheme}://{host}{reverse('cart:pesapal_callback')}"
        cancellation_url = f"{scheme}://{host}{reverse('cart:checkout')}"

        # Split names for billing address
        names = order.full_name.split(' ', 1)
        first_name = names[0] if names else ""
        last_name = names[1] if len(names) > 1 else ""

        # Only include IPN for live
        ipn_id = settings.PESAPAL_NOTIFICATION_ID if env == 'live' else None

        names = order.full_name.split(' ', 1)
        first_name = names[0] if names else ""
        last_name = names[1] if len(names) > 1 else ""
        order_data = {
            "id": order.tx_ref,  # maps to your frontend reference
            "currency": order.currency or "USD",
            "amount": float(order.total),
            "description": f"Book Purchase - Awakening Saints - Order #{order.id}",
            "callback_url": callback_url,
            "cancellation_url": cancellation_url,
            **({"ipn_id": settings.PESAPAL_NOTIFICATION_ID} if env == 'live' else {}),
            "billing_address": {
                "email_address": order.email,
                "phone_number": order.phone,
                "country_code": "UG",
                "first_name": first_name,
                "middle_name": "",
                "last_name": last_name,
                "line_1": order.address or "Not specified",
                "city": order.city or "Kampala",
                "state": "Central",
                "postal_code": "256",
                "zip_code": "256"
            }
        }



        print(f"PesaPal {env.upper()} order data: {order_data}")
        print(f"Sending to PesaPal {env.upper()} URL: {url}")

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.post(url, json=order_data, headers=headers, timeout=30)

        print(f"PesaPal {env.upper()} Response Status: {response.status_code}")
        print(f"PesaPal {env.upper()} Response: {response.text}")

        if response.status_code == 200:
            result = response.json()
            if result.get('redirect_url'):
                # Save PesaPal tracking and redirect info
                order.pesapal_tracking_id = result.get('order_tracking_id')
                order.pesapal_redirect_url = result.get('redirect_url')
                order.save(update_fields=['pesapal_tracking_id', 'pesapal_redirect_url'])

                return JsonResponse({
                    'status': 'success',
                    'redirect_url': result.get('redirect_url'),
                    'order_tracking_id': result.get('order_tracking_id')
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No redirect URL received from PesaPal',
                    'pesapal_response': result
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': f'PesaPal error: {response.status_code} - {response.text}'
            })

    except BookOrder.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Order not found"}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def pesapal_callback(request):
    """
    Handle Pesapal redirect after payment.
    - Receives OrderTrackingId and OrderMerchantReference from Pesapal.
    - Queries Pesapal for payment status and updates the order accordingly.
    - Redirects user to download page if payment is successful.
    - Handles errors and pending/failed payments.
    """
    order_tracking_id = request.GET.get('OrderTrackingId')
    order_merchant_reference = request.GET.get('OrderMerchantReference')
    if not order_tracking_id or not order_merchant_reference:
        messages.error(request, "Missing payment information")
        return redirect('cart:checkout')
    try:
        order = BookOrder.objects.get(tx_ref=order_merchant_reference)
        token = get_pesapal_token()
        if token:
            env = getattr(settings, 'PESAPAL_ENVIRONMENT', 'sandbox').lower()
            if env == 'live':
                base_url = 'https://pay.pesapal.com/v3'
            else:
                base_url = 'https://cybqa.pesapal.com/pesapalv3'
            url = f'{base_url}/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}'
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            print(f"Checking payment status at: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                payment_status = response.json()
                status_code = payment_status.get('status_code', '')
                # Update order status based on PesaPal response
                if status_code == '1':  # Payment completed
                    order.status = 'collected'
                    order.payment_status = 'completed'
                    order.payment_date = timezone.now()
                    order.save()
                    messages.success(request, "Payment successful! Your downloads are ready.")
                    return redirect('cart:download_page', order_id=order.id)
                elif status_code == '0':  # Payment pending
                    order.status = 'pending'
                    order.payment_status = 'pending'
                    order.save()
                    messages.info(request, "Payment is pending. You will be notified when it's completed.")
                    return redirect('cart:order_status', order_id=order.id)
                else:  # Payment failed or cancelled
                    order.status = 'failed'
                    order.payment_status = 'failed'
                    order.save()
                    messages.error(request, "Payment failed. Please try again.")
                    return redirect('cart:checkout')
        # If we can't verify, check if order is already marked as collected
        if order.status == 'collected':
            messages.success(request, "Payment was already processed. Your downloads are ready.")
            return redirect('cart:download_page', order_id=order.id)
        # Default: show pending status
        messages.info(request, "We're verifying your payment. Please check back shortly.")
        return redirect('cart:order_status', order_id=order.id)
    except BookOrder.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect('cart:checkout')
    except Exception as e:
        print(f"Error in pesapal_callback: {e}")
        messages.error(request, "Error processing payment. Please contact support.")
        return redirect('cart:checkout')


# Check order status
@login_required
def order_status(request, order_id):
    """Display order payment status"""
    order = get_object_or_404(BookOrder, id=order_id, email=request.user.email)
    
    # If payment is completed, redirect to downloads
    if order.status == 'collected':
        messages.success(request, "Payment successful! Your downloads are ready.")
        return redirect('cart:download_page', order_id=order.id)
    
    return render(request, 'cart/basketapp/order_status.html', {
        'order': order
    })

# -----------------------------
# Legacy submit_order (for compatibility)
# -----------------------------
@csrf_exempt
@require_POST
def submit_order(request):
    """Legacy endpoint - redirects to new PesaPal flow"""
    try:
        data = json.loads(request.body)
        
        # Generate new reference for PesaPal
        reference = f"PESAPAL-LIVE-{uuid.uuid4().hex[:12].upper()}"
        
        # Return success to trigger frontend PesaPal flow
        return JsonResponse({
            "status": "ok",
            "reference": reference,
            "message": "Proceed with PesaPal payment"
        })
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# -----------------------------
# Download functions
# -----------------------------
def generate_download_link(order_item):
    value = f"{order_item.order.id}:{order_item.product.id}"
    signed_value = signer.sign(value)
    return reverse('cart:download_book', args=[signed_value])

@login_required
def download_book(request, signed_value):
    try:
        value = signer.unsign(signed_value, max_age=1800)
    except SignatureExpired:
        return HttpResponseForbidden("Download link has expired.")
    except BadSignature:
        return HttpResponseForbidden("Invalid download link.")

    order_id, product_id = value.split(':')
    order = get_object_or_404(BookOrder, id=order_id, email=request.user.email, status='collected')
    order_item = get_object_or_404(BookOrderItem, order=order, product_id=product_id)

    if order_item.downloaded:
        return HttpResponseForbidden("This download link has already been used.")

    book_file = order_item.product.book_file
    if not book_file:
        raise Http404("Book file not found")

    order_item.downloaded = True
    order_item.save(update_fields=['downloaded'])

    file_path = book_file.path
    mime_type, _ = mimetypes.guess_type(file_path)

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=mime_type or 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{order_item.product.title}.pdf"'
        return response

@login_required
def download_page(request, order_id):
    order = get_object_or_404(
        BookOrder.objects.prefetch_related('items'),
        id=order_id, email=request.user.email, status='collected'
    )

    links = []
    for item in order.items.all():
        if item.product.book_file and not item.downloaded:
            expires_at = now() + timedelta(minutes=30)
            links.append({
                'title': item.product.title,
                'cover_image': item.product.product_image.url if item.product.product_image else None,
                'order_number': order.id,
                'purchase_date': order.created.strftime("%B %d, %Y %I:%M %p"),
                'author': item.product.author,
                'file_size': f"{item.product.book_file.size / (1024 * 1024):.2f} MB" if item.product.book_file else "N/A",
                'formats': ['PDF'],
                'link': generate_download_link(item),
                'expires_at': expires_at.isoformat()
            })

    return render(request, 'download_page.html', {
        'order': order,
        'links': links
    })

def confirmation(request):
    return render(request, 'cart/basketapp/confirmation.html')

def tracking(request):
    return render(request, 'cart/basketapp/tracking.html')