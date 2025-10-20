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
from django.http import *
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
            'name': product.title, # Assuming 'title' field on Product
            'price': float(product.product_price), # Assuming 'product_price' field on Product
            'qty': item['qty']
        })

    cart_json = json.dumps(cart_items)
    # Pass public key to the template for the Alpine.js component
    context = {
        'cart_json': cart_json,
        'FLUTTERWAVE_PUBLIC_KEY': settings.FLUTTERWAVE_PUBLIC_KEY,
    }
    return render(request, 'cart/basketapp/checkout.html', context)


# -----------------------------
# Submit order (creates pending order)
# -----------------------------
@csrf_exempt
@require_POST
def submit_order(request):
    """
    Receives cart and customer details from frontend,
    creates a pending order in the database, and returns tx_ref.
    """
    try:
        data = json.loads(request.body)

        # Basic validation for required fields
        # Added 'phone_number' to required fields check
        required_fields = ['full_name', 'email', 'phone_number', 'tx_ref', 'cart']
        if not all(field in data for field in required_fields):
            # Improved error message to indicate which fields are missing
            missing_fields = [field for field in required_fields if field not in data]
            return HttpResponseBadRequest(f"Missing required fields: {', '.join(missing_fields)}")

        # Extract customer details from the payload
        full_name = data['full_name']
        email = data['email']
        phone_number = data['phone_number'] # <--- EXTRACT PHONE NUMBER
        tx_ref = data['tx_ref']


        # Calculate total from cart items to prevent client-side tampering
        calculated_total = 0
        for item in data['cart']:
            product_id = item.get('id')
            qty = item.get('qty', 0)
            # It's safer to always get the price from the DB for security and consistency
            # price = item.get('price', 0.0)

            if not product_id or not isinstance(qty, int) or qty <= 0: # Removed price check here
                return HttpResponseBadRequest("Invalid cart item data (product_id or quantity invalid).")

            try:
                product_db = Product.objects.get(pk=product_id)
                calculated_total += qty * float(product_db.product_price) # Use DB price
            except Product.DoesNotExist:
                return HttpResponseBadRequest(f"Product with ID {product_id} not found.")

        # If you have shipping or discount, ensure they are also server-side calculated or validated
        # and then applied to calculated_total BEFORE comparing with frontend_total if you do.
        # For now, let's keep it simple with what's in your BookOrder model
        # Assuming shipping_fee and discount are sent by frontend if applicable, or default to 0
        shipping_fee = float(data.get('shipping_fee', 0))
        discount = float(data.get('discount', 0))
        final_calculated_total = calculated_total + shipping_fee - discount

        # Compare calculated_total with frontend_total (now final_calculated_total with shipping/discount)
        frontend_total = float(data.get('total', 0))
        if abs(final_calculated_total - frontend_total) > 0.01: # Allow for float precision
             print(f"Total mismatch! Calculated: {final_calculated_total}, Frontend: {frontend_total}. Using calculated total.")
             # Decide whether to error out or proceed with calculated_total. Proceeding for now.
             # You might want to return an error here instead:
             # return HttpResponseBadRequest("Total amount mismatch with server calculation.")

        order = BookOrder.objects.create(
            user=request.user if request.user.is_authenticated else None, # Link order to user
            full_name=full_name,
            email=email,
            phone=phone_number, # <--- ADD THIS LINE!
            tx_ref=tx_ref,
            total=final_calculated_total, # Use the final calculated total
            shipping_fee=shipping_fee, # Pass shipping fee if you track it
            discount=discount,       # Pass discount if you track it
            status='pending'
        )

        for item_data in data['cart']:
            try:
                product = Product.objects.get(pk=item_data['id'])
                BookOrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['qty'],
                    price=float(product.product_price) # Always use DB price for order item
                )
            except Product.DoesNotExist:
                # This should ideally not happen if calculated_total passed, but as a safeguard.
                # If an item fails, you might want to rollback the whole order.
                print(f"Product with ID {item_data.get('id')} not found when creating order item.")
                order.delete() # Rollback the parent order
                return HttpResponseBadRequest(f"Product with ID {item_data.get('id')} not found.")
            except Exception as e:
                print(f"Error creating order item: {e}")
                order.delete() # Rollback the parent order
                return HttpResponseServerError({"status": "error", "message": f"Error creating order item: {e}"})

        return JsonResponse({"status": "ok", "order_id": order.id, "tx_ref": order.tx_ref})

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON in request body.")
    except Exception as e:
        print(f"Error submitting order: {e}")
        # Return a JSON error response for better frontend handling
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# -----------------------------
# Payment success (Flutterwave redirect)
# -----------------------------
@login_required
def payment_success(request):
    tx_ref = None
    transaction_id = None # Flutterwave's transaction ID for direct lookup

    print("\n--- Payment Success View Entry Point ---")
    print(f"Request GET parameters: {request.GET}")

    # Attempt 1: Get tx_ref and transaction_id directly from URL query parameters
    tx_ref = request.GET.get("tx_ref")
    transaction_id = request.GET.get("transaction_id") # Flutterwave's transaction_id

    if tx_ref and transaction_id:
        print(f"Attempt 1: Found tx_ref='{tx_ref}' and transaction_id='{transaction_id}' directly.")
    elif tx_ref:
         print(f"Attempt 1: Found tx_ref='{tx_ref}' directly, but no transaction_id. Will rely on API.")


    # Attempt 2: If tx_ref not found, check for the 'resp' parameter (Mobile Money / Sandbox)
    # This often contains more detailed JSON
    if not tx_ref:
        flutterwave_resp_param = request.GET.get("resp")
        if flutterwave_resp_param:
            print(f"Attempt 2: Found 'resp' parameter: {flutterwave_resp_param}")
            try:
                decoded_resp_param = urllib.parse.unquote_plus(flutterwave_resp_param)
                resp_json = json.loads(decoded_resp_param)
                
                data_from_resp = resp_json.get("data", {})
                tx_ref = data_from_resp.get("txRef") or data_from_resp.get("tx_ref")
                transaction_id = data_from_resp.get("id") # Often 'id' in the 'data' part of 'resp'

                print(f"Extracted tx_ref='{tx_ref}' and transaction_id='{transaction_id}' from 'resp' parameter's data.")

                if data_from_resp.get("status") != "successful":
                    messages.info(request, f"Payment status from redirect was '{data_from_resp.get('status')}'. Proceeding to API verification for definitive status.")
                
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error parsing 'resp' parameter: {e}")
                messages.error(request, "Invalid payment response received from Flutterwave (malformed 'resp' parameter).")
                return redirect("cart:checkout")

    # Attempt 3: Fallback - check for 'response' parameter (less common/legacy)
    if not tx_ref:
        flutterwave_legacy_response_param = request.GET.get("response")
        if flutterwave_legacy_response_param:
            print(f"Attempt 3: Found 'response' parameter (legacy fallback): {flutterwave_legacy_response_param}")
            try:
                decoded_legacy_param = urllib.parse.unquote_plus(flutterwave_legacy_response_param)
                legacy_resp_json = json.loads(decoded_legacy_param)
                
                # Try to extract from top-level or 'data' in legacy response
                tx_ref = legacy_resp_json.get("txRef") or legacy_resp_json.get("tx_ref")
                if not tx_ref: # Try data if not at top level
                    tx_ref = legacy_resp_json.get("data", {}).get("txRef") or legacy_resp_json.get("data", {}).get("tx_ref")
                
                transaction_id = legacy_resp_json.get("id") or legacy_resp_json.get("data", {}).get("id")

                print(f"Extracted tx_ref='{tx_ref}' and transaction_id='{transaction_id}' from legacy 'response' parameter.")

                if legacy_resp_json.get("status") != "successful" and legacy_resp_json.get("data",{}).get("status") != "successful":
                    messages.info(request, f"Payment status from legacy redirect was '{legacy_resp_json.get('status', legacy_resp_json.get('data', {}).get('status'))}'. Proceeding to API verification.")

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
    
    # Use verify_by_reference for tx_ref or direct transaction ID verification
    if transaction_id:
        verify_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
        print(f"Verifying using transaction_id: {transaction_id}")
    else:
        verify_url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"
        print(f"Verifying using tx_ref: {tx_ref}")


    try:
        response_obj = requests.get(verify_url, headers=headers, timeout=10)
        response_obj.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        
        verification_response = response_obj.json()
        print(f"Flutterwave verification API response for {tx_ref} / {transaction_id}: {verification_response}")

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
                # Fetching by tx_ref and email ensures the user owns this transaction.
                order = get_object_or_404(BookOrder, tx_ref=tx_ref, email=request.user.email)
            except BookOrder.DoesNotExist:
                messages.error(request, "Order not found or user mismatch. Please contact support.")
                print(f"API Verified but Order not found in DB for tx_ref: {tx_ref} and email: {request.user.email}")
                return redirect("cart:checkout")

            # Validate amount and currency to prevent tampering
            # Use order.total for the expected amount, as calculated server-side during submit_order
            expected_amount = float(order.total)
            actual_amount = float(data.get("amount", 0))
            expected_currency = "USD" # Ensure this matches your order's currency (or order.currency)
            actual_currency = data.get("currency")

            # Use a small tolerance for floating-point comparisons
            if abs(actual_amount - expected_amount) < 0.01 and actual_currency == expected_currency:
                order.status = "collected" # Mark order as paid
                order.flutterwave_id = data.get("id") # Store Flutterwave's internal ID
                order.save(update_fields=["status", "flutterwave_id"])
                
                # Clear the user's cart/basket after successful payment
                # (Assuming cartbasket returns a mutable object or has a clear method)
                basket_to_clear = cartbasket(request)
                if hasattr(basket_to_clear, 'clear'):
                    basket_to_clear.clear() # If your cartbasket has a clear method
                else:
                    # If it's a simple list, you might clear session manually or similar
                    if 'skey' in request.session: # Example if cart is stored under 'skey'
                        del request.session['skey']
                
                messages.success(request, "Payment successful! Your order has been placed and is ready.")
                print(f"Payment for order {order.id} ({tx_ref}) successful and verified. Redirecting to download page.")
                return redirect("cart:download_page", order_id=order.id) # Redirect to a specific order/download page
            else:
                messages.error(request, f"Payment amount or currency mismatch. Potential tampering detected. Please contact support. (Expected: {expected_amount} {expected_currency}, Actual: {actual_amount} {actual_currency})")
                print(f"Amount/currency mismatch for tx_ref: {tx_ref}. Expected: {expected_amount} {expected_currency}, Actual: {actual_amount} {actual_currency}")
                order.status = "failed_verification" # Mark as failed due to mismatch
                order.save(update_fields=["status"])
                return redirect("cart:checkout")
        else:
            messages.info(request, f"Payment status: {data.get('status')}. Your payment was not fully successful. Please check your transaction or try again.")
            print(f"API verification status is not 'successful' for tx_ref: {tx_ref}. Status: {data.get('status')}")
            # Consider updating order status to 'failed' or 'pending_retry'
            try:
                order = get_object_or_404(BookOrder, tx_ref=tx_ref)
                order.status = "failed"
                order.save(update_fields=["status"])
            except BookOrder.DoesNotExist:
                pass # Order might not have been created if tx_ref was forged
            return redirect("cart:checkout")
    else:
        messages.error(request, f"Failed to verify payment with Flutterwave: {verification_response.get('message', 'Unknown error')}")
        print(f"API verification status is not 'success' for tx_ref: {tx_ref}. Response: {verification_response}")
        # Consider updating order status to 'failed'
        try:
            order = get_object_or_404(BookOrder, tx_ref=tx_ref)
            order.status = "failed"
            order.save(update_fields=["status"])
        except BookOrder.DoesNotExist:
            pass
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