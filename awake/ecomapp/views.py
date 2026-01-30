from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.decorators.http import require_POST
from django.conf import settings

from django.http import *
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from .utils import get_media_duration  # if using separate utils file

import requests
from itertools import islice
from django.core.mail import send_mass_mail

# --- Pesapal Integration (API v3, OAuth2) ---
# See: https://developer.pesapal.com/how-to-integrate/api-v3/overview
# This implementation uses the correct OAuth2 token flow and official endpoints.

import base64
import os  # For environment variables
import uuid  # For unique transaction references
import logging  # For logging payment attempts and errors

# Helper: Get OAuth2 access token from Pesapal

def get_pesapal_access_token():
    """
    Obtain OAuth2 access token from Pesapal using client credentials grant.
    """
    consumer_key = os.environ.get('PESAPAL_CONSUMER_KEY', getattr(settings, 'PESAPAL_CONSUMER_KEY', ''))
    consumer_secret = os.environ.get('PESAPAL_CONSUMER_SECRET', getattr(settings, 'PESAPAL_CONSUMER_SECRET', ''))
    environment = getattr(settings, 'PESAPAL_ENVIRONMENT', 'sandbox')
    if not consumer_key or not consumer_secret:
        raise Exception('Pesapal credentials are required. Set PESAPAL_CONSUMER_KEY and PESAPAL_CONSUMER_SECRET.')
    if environment == 'live':
        token_url = 'https://pay.pesapal.com/v3/api/Auth/RequestToken'
    else:
        token_url = 'https://sandbox.pesapal.com/v3/api/Auth/RequestToken'
    auth_header = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/json',
    }
    resp = requests.get(token_url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.json().get('token')

def indexone(request):
    return render(request, 'site/index.html')

def about(request):
    return render(request, 'site/about.html')

def contactone(request):
    return render(request, 'site/contact.html')

def services(request):
    return render(request, 'site/services.html')

def donate(request):
    return render(request, 'site/donate.html')

def orphans(request):
    return render(request, 'site/organisation.html')

def books(request):
    return render(request, 'site/books.html')


def media(request):
    media_items = SermonContent.objects.all()

    def serialize(media):
        duration = "00:00"
        if media.media_type in ['audio', 'video'] and media.file:
            try:
                file_path = media.file.path
                duration = get_media_duration(file_path, media.media_type)
            except Exception:
                duration = "00:00"

        text_body = media.text_body or ""
        pages = text_body.split('\n\n') if '\n\n' in text_body else [text_body] if text_body else []

        return {
            "id": media.id,
            "type": media.media_type,
            "title": media.title,
            "artist": media.preacher or "Uploaded by Admin",
            "duration": duration,
            "date": media.uploaded_at.strftime('%b %d, %Y'),
            "description": media.description or "No description yet.",
            "scripture": media.scripture or "",
            "src": media.get_file_url(),
            "thumbnail": media.get_thumbnail_url(),
            "excerpt": media.get_excerpt(),
            "text_body": text_body,
            "expanded": False,
            "currentPage": 0,
            "pages": pages,
            "comments": [
                {
                    "username": comment.user.first_name or comment.user.last_name,
                    "text": comment.comment,
                    "timestamp": comment.timestamp.strftime('%b %d, %Y'),
                }
                for comment in media.comments.all().order_by('-timestamp')
            ],
        }

    audios = [serialize(m) for m in media_items.filter(media_type='audio')]
    videos = [serialize(m) for m in media_items.filter(media_type='video')]
    texts = [serialize(m) for m in media_items.filter(media_type='text')]

    context = {
        'audio_json': json.dumps(audios, cls=DjangoJSONEncoder),
        'video_json': json.dumps(videos, cls=DjangoJSONEncoder),
        'text_json': json.dumps(texts, cls=DjangoJSONEncoder),
    }

    return render(request, 'site/media.html', context)


@csrf_exempt  # Optional if you're passing CSRF tokens via JS
@login_required
def add_comment(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        media_id = data.get('media_id')
        comment_text = data.get('comment')

        if not media_id or not comment_text.strip():
            return JsonResponse({'status': 'error', 'message': 'Missing comment or media ID'}, status=400)

        media = SermonContent.objects.get(id=media_id)
        comment = SermonComment.objects.create(
            user=request.user,
            media=media,
            comment=comment_text.strip(),
            timestamp=timezone.now()
        )

        return JsonResponse({
            'status': 'ok',
            'comment': {
                'username': request.user.first_name or request.user.last_name,
                'text': comment.comment,
                'timestamp': 'Just now'
            }
        })

    except SermonContent.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Media not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



def index(request, cat_slug=None):
    if cat_slug:
        category = get_object_or_404(Category, cat_slug=cat_slug)
        products = Product.objects.filter(category=category, is_active=True)
    else:
        products = Product.products.all()

    product_data = [{
        "id": p.id,
        "title": p.title,
        "author": p.author,
        "price": float(p.product_price),
        "image": p.product_image.url if p.product_image else '',
        "category_name": p.category.cat_name,
        "category_slug": p.category.cat_slug,
        "rating": 4.5,  # placeholder
        "slug": p.product_slug,
    } for p in products]

    categories = Category.objects.all()
    category_data = [{"name": cat.cat_name, "slug": cat.cat_slug} for cat in categories]

    context = {
        "slider": products,
        "products": products,  # Add this for Jinja2 rendering
        "products_json": json.dumps(product_data),
        "categories_json": json.dumps(category_data),
    }
    return render(request, 'main/ecomapp/index.html', context)


def single_product(request, product_slug):
    product = get_object_or_404(Product, product_slug = product_slug, in_stock=True)
    reviews = product.reviews.select_related('user').order_by('-timestamp')
    context = {'product':product,  'reviews': reviews,}
    return render(request, 'main/ecomapp/single-product.html', context)


@csrf_exempt
@login_required
def add_review_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rating = int(data.get('rating', 0))
            comment = data.get('comment', '').strip()
            book_id = data.get('book_id')

            if not (1 <= rating <= 5):
                return JsonResponse({'success': False, 'error': 'Invalid rating.'})

            book = Product.objects.get(id=book_id)

            review = BookReview.objects.create(
                user=request.user,
                book=book,
                rating=rating,
                comment=comment
            )

            return JsonResponse({
                'success': True,
                'username': request.user.get_full_name() or request.user.username,
                'rating': rating,
                'comment': comment
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def book_preview(request, product_slug):
    product = get_object_or_404(Product, product_slug=product_slug, in_stock=True)
    preview = get_object_or_404(BookPreview, book=product)

    context = {
        'product': product,
        'preview': preview,
    }
    return render(request, 'main/ecomapp/preview.html', context)



# subscriptions/views.py
def send_message_to_subscribers(request, message_id):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=401)

    message = get_object_or_404(SubscriberMessage, id=message_id)
    subscribers = EmailSubscriber.objects.all()

    subject = message.title
    body = message.body
    from_email = settings.DEFAULT_FROM_EMAIL

    messages = [
        (subject, body, from_email, [sub.email])
        for sub in subscribers
    ]

    send_mass_mail(messages, fail_silently=False)
    return render(request, 'admin/success_mail.html')
    # return HttpResponse("Emails sent successfully.")


@csrf_exempt
def subscribe_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            EmailSubscriber.objects.get_or_create(email=email)
        return HttpResponseRedirect("/?subscribed_successfully=1")
    return HttpResponseRedirect("/?subscription_not_successfully=0")






def contact(request):
    return render(request, 'main/ecomapp/contact.html')

def blog(request):
    return render(request, 'main/ecomapp/blog.html')

def single_blog(request):
    return render(request, 'main/ecomapp/single-blog.html')


# --- Pesapal Payment Request View (API v3) ---
def pesapal_payment_request(request):
    """
    Initiates a Pesapal payment request and redirects user to Pesapal hosted payment page.
    Uses OAuth2 token and v3 endpoint.
    """
    if request.method == 'POST':
        amount = request.POST.get('amount')
        currency = getattr(settings, 'DEFAULT_CURRENCY', 'USD')
        description = request.POST.get('description', 'Order Payment')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        tx_ref = str(uuid.uuid4())
        order = BookOrder.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            tx_ref=tx_ref,
            total=amount,
            currency=currency,
            payment_status=BookOrder.PAYMENT_PENDING,
            status=BookOrder.STATUS_PENDING,
        )
        callback_url = request.build_absolute_uri(reverse('sales:pesapal_callback'))
        ipn_url = request.build_absolute_uri(reverse('sales:pesapal_ipn'))
        environment = getattr(settings, 'PESAPAL_ENVIRONMENT', 'sandbox')
        if environment == 'live':
            pesapal_api_url = 'https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest'
        else:
            pesapal_api_url = 'https://sandbox.pesapal.com/v3/api/Transactions/SubmitOrderRequest'
        # Get OAuth2 token
        try:
            access_token = get_pesapal_access_token()
        except Exception as e:
            return render(request, 'main/ecomapp/payment_error.html', {'error': f'Pesapal Auth Error: {e}'})
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        data = {
            "id": tx_ref,
            "currency": currency,
            "amount": amount,
            "description": description,
            "callback_url": callback_url,
            "notification_id": getattr(settings, 'PESAPAL_NOTIFICATION_ID', ''),
            "customer": {
                "email_address": email,
                "phone_number": phone,
                "first_name": full_name,
                "last_name": "",
            },
        }
        try:
            response = requests.post(pesapal_api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            resp_json = response.json()
            order_tracking_id = resp_json.get('order_tracking_id')
            redirect_url = resp_json.get('redirect_url')
            order.pesapal_tracking_id = order_tracking_id
            order.pesapal_redirect_url = redirect_url
            order.save()
            PaymentLog.objects.create(
                order=order,
                pesapal_tracking_id=order_tracking_id,
                status_code='INIT',
                status_description='Payment initiated',
                ipn_data=resp_json,
            )
            return redirect(redirect_url)
        except Exception as e:
            logging.exception('Pesapal payment request failed')
            return render(request, 'main/ecomapp/payment_error.html', {'error': str(e)})
    else:
        # Render a payment form (example only)
        return render(request, 'main/ecomapp/payment_form.html')

# --- Pesapal Callback View (unchanged) ---
def pesapal_callback(request):
    """
    Handles Pesapal redirect after payment (user-facing). Does NOT mark payment as successful.
    """
    order_tracking_id = request.GET.get('OrderTrackingId')
    merchant_reference = request.GET.get('merchant_reference')
    # Optionally, show a thank you or processing page
    return render(request, 'main/ecomapp/payment_callback.html', {
        'order_tracking_id': order_tracking_id,
        'merchant_reference': merchant_reference,
    })

# --- Pesapal IPN Endpoint (API v3, OAuth2) ---
@csrf_exempt
@require_POST
def pesapal_ipn(request):
    """
    Receives IPN from Pesapal, verifies payment, and updates order if COMPLETED.
    Uses OAuth2 token and v3 endpoint.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        order_tracking_id = data.get('OrderTrackingId')
        merchant_reference = data.get('merchant_reference')
        order = BookOrder.objects.get(pesapal_tracking_id=order_tracking_id, tx_ref=merchant_reference)
        environment = getattr(settings, 'PESAPAL_ENVIRONMENT', 'sandbox')
        if environment == 'live':
            status_url = f'https://pay.pesapal.com/v3/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}'
        else:
            status_url = f'https://sandbox.pesapal.com/v3/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}'
        try:
            access_token = get_pesapal_access_token()
        except Exception as e:
            logging.exception('Pesapal Auth Error')
            return HttpResponse('ERROR', status=200)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        status_resp = requests.get(status_url, headers=headers, timeout=30)
        status_resp.raise_for_status()
        status_json = status_resp.json()
        payment_status = status_json.get('status')
        PaymentLog.objects.create(
            order=order,
            pesapal_tracking_id=order_tracking_id,
            status_code=payment_status,
            status_description='IPN received',
            ipn_data=status_json,
        )
        if payment_status and payment_status.lower() == 'completed':
            order.payment_status = BookOrder.PAYMENT_COMPLETED
            order.save()
        elif payment_status and payment_status.lower() == 'failed':
            order.payment_status = BookOrder.PAYMENT_FAILED
            order.save()
        return HttpResponse('OK', status=200)
    except Exception as e:
        logging.exception('Pesapal IPN processing failed')
        return HttpResponse('ERROR', status=200)
# --- END Pesapal Integration ---
# NOTE: Use your real Pesapal credentials in environment variables for production.



