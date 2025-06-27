from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.decorators.http import require_POST

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json



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

def media(request):
    return render(request, 'site/media.html')

def books(request):
    return render(request, 'site/books.html')


def index(request):
    products = Product.products .all()
    context = {
        'products':products,
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







def shop(request, cat_slug):
    category = get_object_or_404(Category, cat_slug = cat_slug)
    products = Product.objects.filter(category=category)
    context = {
      'category':category,
      'products':products
    }
    return render(request, 'main/ecomapp/category.html', context)









def contact(request):
    return render(request, 'main/ecomapp/contact.html')

def blog(request):
    return render(request, 'main/ecomapp/blog.html')

def single_blog(request):
    return render(request, 'main/ecomapp/single-blog.html')



