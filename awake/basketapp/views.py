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
import requests
from django.conf import settings
import urllib.request     # for opening URLs (urllib.request.urlopen, etc.)
import urllib.parse       # for parsing URLs or encoding parameters
import urllib.error       # for catching HTTPError or URLError

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

        # Calculate total quantity in cart
        total_qty = len(basket)  # or use sum(item['qty'] for item in basket.basket.values())

        return JsonResponse({
            'message': 'Product added',
            'product_id': product_id,
            'qty': product_qty,
            'cart_count': total_qty  # end this to update the icon
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
                product_qty = 1  # optional: prevent 0 or negative quantities
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid input'}, status=400)

        basket.update(product=product_id, qty=product_qty)

        return JsonResponse({
            'cart_count': len(basket),  # total items in cart
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
            'cart_count': len(cart)  # 👈 use 'cart_count'
        })
    return JsonResponse({'error': 'Invalid action'}, status=400)


# def checkout(request):
#     return render(request, 'cart/basketapp/checkout.html')



# -----------------------------
# Checkout view (optional if using Alpine.js for front-end)
# -----------------------------
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
# Submit order (creates pending order)
# -----------------------------
@csrf_exempt
@require_POST
def submit_order(request):
    try:
        data = json.loads(request.body)

        order = BookOrder.objects.create(
            full_name=data['full_name'],
            email=data['email'],
            phone=data.get('phone', ''),
            tx_ref=data['tx_ref'],
            total=data.get('total', 0),
            status='pending'
        )

        for item in data['cart']:
            product = Product.objects.get(pk=item['id'])
            BookOrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['qty'],
                price=item['price']
            )

        return JsonResponse({"status": "ok", "order_id": order.id})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# -----------------------------
# Payment success (Flutterwave redirect)
# -----------------------------

@login_required
def payment_success(request):
    tx_ref = None

    # --- Debugging Start ---
    print("\n--- Payment Success View Entry Point ---")
    print(f"Request GET parameters: {request.GET}")
    # --- Debugging End ---

    # Attempt 1: Get tx_ref directly from the URL query parameters
    # This is common for card payments and some Flutterwave redirects
    tx_ref = request.GET.get("tx_ref")
    if tx_ref:
        print(f"Attempt 1: Found tx_ref directly: {tx_ref}")

    # Attempt 2: If tx_ref not found, check for the 'resp' parameter (Mobile Money / Sandbox)
    # This is based on your debug output for mobile money
    if not tx_ref:
        flutterwave_resp_param = request.GET.get("resp")
        if flutterwave_resp_param:
            print(f"Attempt 2: Found 'resp' parameter: {flutterwave_resp_param}")
            try:
                decoded_resp_param = urllib.parse.unquote_plus(flutterwave_resp_param)
                resp_json = json.loads(decoded_resp_param)
                # print(f"Parsed 'resp' JSON: {resp_json}")

                # Extract tx_ref from the 'data' key within the JSON response
                data_from_resp = resp_json.get("data", {})
                tx_ref = data_from_resp.get("txRef") or data_from_resp.get("tx_ref")
                
                # print(f"Extracted tx_ref from 'resp' parameter's data: {tx_ref}")

                # Optional: Early check for payment status from the redirect (good for immediate feedback)
                # However, the API verification is the definitive source.
                if data_from_resp.get("status") != "successful":
                    messages.info(request, f"Payment status from redirect: {data_from_resp.get('status')}. We'll try to verify it.")
                    # Do not return yet, proceed to API verification as it's more reliable
                    print(f"Early status check from 'resp' JSON was not 'successful' for tx_ref: {tx_ref}. Proceeding to API verification.")

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error parsing 'resp' parameter: {e}")
                print(f"Raw 'resp' parameter: {flutterwave_resp_param}")
                messages.error(request, "Invalid payment response received from Flutterwave (malformed 'resp' parameter).")
                return redirect("cart:checkout")

    # Attempt 3: Fallback - check for 'response' parameter (less common, but good to have)
    # This was in your original code, and while 'resp' was the actual one,
    # it doesn't hurt to keep 'response' as a very low priority fallback.
    if not tx_ref:
        flutterwave_legacy_response_param = request.GET.get("response")
        if flutterwave_legacy_response_param:
            print(f"Attempt 3: Found 'response' parameter (legacy fallback): {flutterwave_legacy_response_param}")
            try:
                decoded_legacy_param = urllib.parse.unquote_plus(flutterwave_legacy_response_param)
                legacy_resp_json = json.loads(decoded_legacy_param)
                print(f"Parsed legacy 'response' JSON: {legacy_resp_json}")
                
                # Try to extract from top-level or 'data' in legacy response
                tx_ref = legacy_resp_json.get("txRef") or legacy_resp_json.get("tx_ref")
                if not tx_ref: # Try data if not at top level
                    tx_ref = legacy_resp_json.get("data", {}).get("txRef") or legacy_resp_json.get("data", {}).get("tx_ref")

                print(f"Extracted tx_ref from legacy 'response' parameter: {tx_ref}")

                if legacy_resp_json.get("status") != "successful" and legacy_resp_json.get("data",{}).get("status") != "successful":
                    messages.info(request, f"Payment status from legacy redirect: {legacy_resp_json.get('status', legacy_resp_json.get('data', {}).get('status'))}. We'll try to verify it.")
                    print(f"Early status check from legacy 'response' JSON was not 'successful' for tx_ref: {tx_ref}. Proceeding to API verification.")

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error parsing legacy 'response' parameter: {e}")
                messages.error(request, "Invalid payment response received from Flutterwave (malformed legacy 'response' parameter).")
                return redirect("cart:checkout")

    # Final check: If after all attempts, tx_ref is still missing, we cannot proceed
    if not tx_ref:
        messages.error(request, "Transaction reference missing. Cannot verify payment. Please contact support if this persists.")
        print("Final Fallback: No tx_ref found after all attempts. Redirecting to checkout.")
        return redirect("cart:checkout")

    # --- Proceed to verify transaction via Flutterwave API ---
    print(f"\n--- Proceeding to API Verification for tx_ref: {tx_ref} ---")
    headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
    verify_url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"

    try:
        response_obj = requests.get(verify_url, headers=headers, timeout=10)
        response_obj.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        
        verification_response = response_obj.json()
        print(f"Flutterwave verification API response for {tx_ref}: {verification_response}")

    except requests.exceptions.HTTPError as e:
        error_msg = f"Flutterwave verification failed (HTTP Error: {e.response.status_code}). Please try again."
        print(f"{error_msg} - Details: {e.response.text}")
        messages.error(request, error_msg)
        return redirect("cart:checkout")
    except json.JSONDecodeError as e:
        error_msg = "Flutterwave API returned an unreadable response. Please contact support."
        print(f"{error_msg} - Details: {e} - Raw: {response_obj.text}")
        messages.error(request, error_msg)
        return redirect("cart:checkout")
    except requests.RequestException as e:
        error_msg = "Payment verification failed due to network error. Please try again."
        print(f"{error_msg} - Details: {e}")
        messages.error(request, error_msg)
        return redirect("cart:checkout")

    # --- Process successful API verification response ---
    if verification_response.get("status") == "success":
        data = verification_response.get("data", {}) # This 'data' is from the API verification
        
        if data.get("status") == "successful":
            try:
                # IMPORTANT: Ensure the order exists and belongs to the current user
                order = get_object_or_404(BookOrder, tx_ref=tx_ref, email=request.user.email)
            except BookOrder.DoesNotExist:
                messages.error(request, "Order not found or user mismatch. Please contact support.")
                print(f"API Verified but Order not found in DB for tx_ref: {tx_ref} and email: {request.user.email}")
                return redirect("cart:checkout")

            # Validate amount and currency to prevent tampering
            expected_amount = float(order.total)
            actual_amount = float(data.get("amount", 0))
            expected_currency = "USD" # Ensure this matches your order's currency
            actual_currency = data.get("currency")

            if actual_amount >= expected_amount and actual_currency == expected_currency:
                order.status = "collected" # Mark order as paid
                order.save(update_fields=["status"])
                messages.success(request, "Payment successful! Your downloads are ready.")
                print(f"Payment for order {order.id} ({tx_ref}) successful and verified. Redirecting to download page.")
                return redirect("cart:download_page", order_id=order.id)
            else:
                messages.error(request, "Payment amount or currency mismatch. Potential tampering detected.")
                print(f"Amount/currency mismatch for tx_ref: {tx_ref}. Expected: {expected_amount} {expected_currency}, Actual: {actual_amount} {actual_currency}")
                return redirect("cart:checkout")
        else:
            messages.info(request, f"Payment status: {data.get('status')}. Please check your transaction or try again.")
            print(f"API verification status is not 'successful' for tx_ref: {tx_ref}. Status: {data.get('status')}")
            return redirect("cart:checkout")
    else:
        messages.error(request, f"Failed to verify payment with Flutterwave: {verification_response.get('message', 'Unknown error')}")
        print(f"API verification status is not 'success' for tx_ref: {tx_ref}. Response: {verification_response}")
        return redirect("cart:checkout")

    # Generic catch-all for unexpected scenarios
    messages.error(request, "An unexpected error occurred during payment processing. Please contact support.")
    print(f"Unexpected error at the end of payment_success view for tx_ref: {tx_ref} (or None if not found).")
    return redirect("cart:checkout")

# @login_required
# def payment_success(request):
#     tx_ref = request.GET.get("tx_ref") # Try to get tx_ref directly first

#     # If tx_ref is not found directly, check for the 'response' parameter
#     if not tx_ref:
#         flutterwave_response_param = request.GET.get("response")
#         if flutterwave_response_param:
#             try:
#                 # URL-decode the parameter value before loading JSON
#                 decoded_response_param = urllib.parse.unquote_plus(flutterwave_response_param)
#                 resp_json = json.loads(decoded_response_param)
                
#                 # Extract txRef from the top level of the JSON response
#                 tx_ref = resp_json.get("txRef") or resp_json.get("tx_ref")
                
#                 # --- IMPORTANT DEBUGGING STEP ---
#                 # Log the parsed redirect response. Check if tx_ref is truly there.
#                 print(f"Parsed Flutterwave redirect 'response' parameter: {resp_json}")
#                 print(f"Extracted tx_ref from redirect 'response': {tx_ref}")

#                 # Early check for payment status from the redirect (API verification is still definitive)
#                 if resp_json.get("status") != "successful":
#                     messages.error(request, f"Payment not marked as successful in Flutterwave redirect. Status: {resp_json.get('status')}")
#                     return redirect("cart:checkout")

#             except (json.JSONDecodeError, KeyError, TypeError) as e:
#                 print(f"Error parsing Flutterwave 'response' parameter: {e}")
#                 print(f"Raw 'response' parameter: {flutterwave_response_param}")
#                 messages.error(request, "Invalid payment response received from Flutterwave.")
#                 return redirect("cart:checkout")
        
#     # If after all attempts, tx_ref is still missing
#     if not tx_ref:
#         messages.error(request, "Transaction reference missing. Cannot verify payment.")
#         return redirect("cart:checkout")

#     # Proceed to verify transaction via Flutterwave API using the extracted tx_ref
#     headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
#     verify_url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"

#     try:
#         response_obj = requests.get(verify_url, headers=headers, timeout=10)
        
#         # --- NEW ROBUST HANDLING ---
#         # 1. Check HTTP status code first
#         response_obj.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        
#         # 2. Try to parse JSON. If it fails, the response was not JSON.
#         verification_response = response_obj.json()
#         print(f"Flutterwave verification API response for {tx_ref}: {verification_response}")
#         # --- END NEW ROBUST HANDLING ---

#     except requests.exceptions.HTTPError as e:
#         print(f"Flutterwave API returned HTTP Error: {e.response.status_code} - {e.response.text}")
#         messages.error(request, f"Flutterwave verification failed (HTTP Error: {e.response.status_code}). Please try again.")
#         return redirect("cart:checkout")
#     except json.JSONDecodeError as e:
#         print(f"Flutterwave API response was not valid JSON: {e}")
#         print(f"Raw API response text: {response_obj.text}") # Log the raw text here!
#         messages.error(request, "Flutterwave API returned an unreadable response. Please contact support.")
#         return redirect("cart:checkout")
#     except requests.RequestException as e:
#         print(f"Request to Flutterwave API failed: {e}")
#         messages.error(request, "Payment verification failed due to network error. Please try again.")
#         return redirect("cart:checkout")

#     # Process successful JSON verification response
#     if verification_response.get("status") == "success":
#         data = verification_response.get("data", {})
        
#         if data.get("status") == "successful":
#             try:
#                 order = get_object_or_404(BookOrder, tx_ref=tx_ref, email=request.user.email)
#             except BookOrder.DoesNotExist:
#                 messages.error(request, "Order not found or user mismatch.")
#                 return redirect("cart:checkout")

#             expected_amount = float(order.total)
#             actual_amount = float(data.get("amount", 0))
#             expected_currency = "UGX" # Adjust if your order model stores currency
#             actual_currency = data.get("currency")

#             if actual_amount >= expected_amount and actual_currency == expected_currency:
#                 order.status = "collected"
#                 order.save(update_fields=["status"])
#                 messages.success(request, "Payment successful! Your downloads are ready.")
#                 return redirect("cart:download_page", order_id=order.id)
#             else:
#                 messages.error(request, "Payment amount or currency mismatch. Potential tampering detected.")
#                 return redirect("cart:checkout")
#         else:
#             messages.info(request, f"Payment status: {data.get('status')}. Please check your transaction or try again.")
#             return redirect("cart:checkout")
#     else:
#         messages.error(request, f"Failed to verify payment with Flutterwave: {verification_response.get('message', 'Unknown error')}")
#         return redirect("cart:checkout")

#     messages.error(request, "An unexpected error occurred during payment processing. Please contact support.")
#     return redirect("cart:checkout")

# @login_required
# def payment_success(request):
#     # 1️⃣ Try to get resp (sandbox)
#     resp_param = request.GET.get("resp")
#     tx_ref = None

#     if resp_param:
#         try:
#             resp_json = json.loads(resp_param)
#             data = resp_json.get("data", {})
#             tx_ref = data.get("txRef") or data.get("tx_ref")
#         except json.JSONDecodeError:
#             messages.error(request, "Invalid payment response.")
#             return redirect("cart:checkout")
    
#     # 2️⃣ Fallback for live accounts (redirect sends tx_ref)
#     if not tx_ref:
#         tx_ref = request.GET.get("tx_ref")
    
#     if not tx_ref:
#         messages.error(request, "Transaction reference missing.")
#         return redirect("cart:checkout")

#     # 3️⃣ Verify transaction via Flutterwave API
#     headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
#     verify_url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"

#     try:
#         verification = requests.get(verify_url, headers=headers, timeout=10).json()
#     except requests.RequestException:
#         messages.error(request, "Payment verification failed. Please try again.")
#         return redirect("cart:checkout")

#     # 4️⃣ Check successful payment
#     if verification.get("status") == "success" and verification["data"]["status"] == "successful":
#         order = get_object_or_404(BookOrder, tx_ref=tx_ref, email=request.user.email)
#         order.status = "collected"
#         order.save(update_fields=["status"])
#         return redirect("cart:download_page", order_id=order.id)

#     messages.error(request, "Payment could not be verified. Please contact support.")
#     return redirect("cart:checkout")

# -----------------------------
# Generate download link
# -----------------------------
def generate_download_link(order_item):
    value = f"{order_item.order.id}:{order_item.product.id}"
    signed_value = signer.sign(value)
    return reverse('cart:download_book', args=[signed_value])


# -----------------------------
# Download individual book
# -----------------------------
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


# -----------------------------
# Download page (all pending downloads)
# -----------------------------
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
                'purchase_date': order.created.strftime("%B %d, %Y %I:%M %p"),  # e.g., October 06, 2025 11:30 AM
                'author': item.product.author,
                'file_size': f"{item.product.book_file.size / (1024 * 1024):.2f} MB" if item.product.book_file else "N/A",
                'formats': ['PDF'],  # Extend if multiple formats are available
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