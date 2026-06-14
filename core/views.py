# core/views.py
import csv
import json
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, F, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sitemaps import Sitemap
from django.conf import settings

from .models import (
    Category, Tag, Link, LinkVersion, ClickLog,
    Rating, Bookmark, Report, Feedback, BrowsingHistory
)
from .forms import (
    AdminLoginForm, CategoryForm, LinkForm,
    CSVImportForm, ReportForm, FeedbackForm
)


def is_admin(user):
    return user.is_staff or user.is_superuser


def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def expand_search_query(query):
    """Expand search query with synonyms"""
    synonyms = getattr(settings, 'SEARCH_SYNONYMS', {})
    query_lower = query.lower().strip()
    expanded = [query_lower]
    for key, values in synonyms.items():
        if query_lower == key or query_lower in values:
            expanded.append(key)
            expanded.extend(values)
    return list(set(expanded))


# ============ PUBLIC VIEWS ============

def index(request):
    """Main public page"""
    categories = Category.objects.filter(is_active=True).annotate(
        total_links=Count('links', filter=Q(links__is_active=True))
    )

    # Base queryset
    links = Link.objects.filter(is_active=True).prefetch_related('categories', 'tags')

    # Filtering
    selected_category = request.GET.get('category', '')
    selected_tag = request.GET.get('tag', '')
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'newest')

    if selected_category:
        links = links.filter(categories__slug=selected_category)

    if selected_tag:
        links = links.filter(tags__slug=selected_tag)

    if search_query:
        expanded = expand_search_query(search_query)
        q_filter = Q()
        for term in expanded:
            q_filter |= (
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(tags__name__icontains=term) |
                Q(categories__name__icontains=term)
            )
        links = links.filter(q_filter).distinct()

    # Sorting
    if sort_by == 'popular':
        links = links.order_by('-click_count')
    elif sort_by == 'rating':
        links = links.order_by('-avg_rating')
    elif sort_by == 'az':
        links = links.order_by('title')
    elif sort_by == 'oldest':
        links = links.order_by('created_at')
    else:
        links = links.order_by('-is_featured', '-created_at')

    links = links.distinct()

    # Featured links
    featured_links = Link.objects.filter(is_active=True, is_featured=True)[:8]

    # Popular links
    popular_links = Link.objects.filter(is_active=True).order_by('-click_count')[:10]

    # Recently added (this week)
    week_ago = timezone.now() - timedelta(days=7)
    recent_links = Link.objects.filter(is_active=True, created_at__gte=week_ago).order_by('-created_at')[:10]

    # All tags
    tags = Tag.objects.annotate(
        total_links=Count('links', filter=Q(links__is_active=True))
    ).filter(total_links__gt=0).order_by('-total_links')

    # User bookmarks
    session_key = get_session_key(request)
    bookmarked_ids = list(
        Bookmark.objects.filter(session_key=session_key).values_list('link_id', flat=True)
    )

    # Recently visited
    history = BrowsingHistory.objects.filter(
        session_key=session_key
    ).select_related('link').order_by('-visited_at')[:10]

    # Stats
    total_links = Link.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    total_clicks = sum(Link.objects.filter(is_active=True).values_list('click_count', flat=True))

    context = {
        'categories': categories,
        'links': links,
        'featured_links': featured_links,
        'popular_links': popular_links,
        'recent_links': recent_links,
        'tags': tags,
        'selected_category': selected_category,
        'selected_tag': selected_tag,
        'search_query': search_query,
        'sort_by': sort_by,
        'bookmarked_ids': bookmarked_ids,
        'history': history,
        'total_links': total_links,
        'total_categories': total_categories,
        'total_clicks': total_clicks,
    }
    return render(request, 'core/index.html', context)


def track_click(request, link_id):
    """Track click and redirect"""
    link = get_object_or_404(Link, id=link_id, is_active=True)
    link.click_count = F('click_count') + 1
    link.save(update_fields=['click_count'])

    session_key = get_session_key(request)

    ClickLog.objects.create(
        link=link,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        session_key=session_key
    )

    BrowsingHistory.objects.update_or_create(
        link=link,
        session_key=session_key,
        defaults={'visited_at': timezone.now()}
    )

    return redirect(link.url)


def auto_suggest(request):
    """AJAX auto-suggest endpoint"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    expanded = expand_search_query(query)
    q_filter = Q()
    for term in expanded:
        q_filter |= Q(title__icontains=term) | Q(description__icontains=term)

    links = Link.objects.filter(q_filter, is_active=True).distinct()[:8]
    results = [
        {
            'id': l.id,
            'title': l.title,
            'description': l.description[:80],
            'favicon': l.favicon,
            'categories': list(l.categories.values_list('name', flat=True)),
        }
        for l in links
    ]
    return JsonResponse({'results': results})


@require_POST
def toggle_bookmark(request, link_id):
    """Toggle bookmark via AJAX"""
    link = get_object_or_404(Link, id=link_id)
    session_key = get_session_key(request)

    bookmark, created = Bookmark.objects.get_or_create(
        link=link, session_key=session_key
    )
    if not created:
        bookmark.delete()
        return JsonResponse({'bookmarked': False})
    return JsonResponse({'bookmarked': True})


@require_POST
def rate_link(request, link_id):
    """Rate a link via AJAX"""
    link = get_object_or_404(Link, id=link_id)
    session_key = get_session_key(request)
    score = int(request.POST.get('score', 0))

    if score < 1 or score > 5:
        return JsonResponse({'error': 'Invalid rating'}, status=400)

    Rating.objects.update_or_create(
        link=link, session_key=session_key,
        defaults={'score': score}
    )

    avg = link.ratings.aggregate(avg=Avg('score'))['avg'] or 0
    total = link.ratings.count()
    link.avg_rating = round(avg, 1)
    link.total_ratings = total
    link.save(update_fields=['avg_rating', 'total_ratings'])

    return JsonResponse({'avg_rating': link.avg_rating, 'total_ratings': total})


@require_POST
def submit_report(request, link_id):
    """Submit a report for a link"""
    link = get_object_or_404(Link, id=link_id)
    form = ReportForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False)
        report.link = link
        report.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def submit_feedback(request):
    """Submit general feedback"""
    form = FeedbackForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


def service_page(request, slug):
    """SEO-friendly service page"""
    link = get_object_or_404(Link, slug=slug, is_active=True)
    session_key = get_session_key(request)
    is_bookmarked = Bookmark.objects.filter(link=link, session_key=session_key).exists()
    user_rating = Rating.objects.filter(link=link, session_key=session_key).first()
    similar = Link.objects.filter(
        categories__in=link.categories.all(), is_active=True
    ).exclude(id=link.id).distinct()[:5]

    context = {
        'link': link,
        'is_bookmarked': is_bookmarked,
        'user_rating': user_rating,
        'similar_links': similar,
    }
    return render(request, 'core/index.html', context)


def category_page(request, slug):
    """SEO-friendly category page — redirects to index with filter"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    return redirect(f'/?category={category.slug}')


def get_bookmarks(request):
    """Get user's bookmarked links"""
    session_key = get_session_key(request)
    bookmarks = Bookmark.objects.filter(session_key=session_key).select_related('link')
    bookmark_ids = [b.link_id for b in bookmarks]
    return JsonResponse({'bookmark_ids': bookmark_ids})


# ============ ADMIN VIEWS ============

def admin_login_view(request):
    """Hidden admin login page"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if is_admin(user):
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'You do not have admin privileges.')
        else:
            messages.error(request, 'Invalid credentials.')
    else:
        form = AdminLoginForm()

    return render(request, 'core/admin_login.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def admin_logout_view(request):
    logout(request)
    return redirect('index')


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard - handles everything"""
    # Stats
    total_links = Link.objects.count()
    active_links = Link.objects.filter(is_active=True).count()
    broken_links = Link.objects.filter(link_status='broken').count()
    total_clicks = sum(Link.objects.values_list('click_count', flat=True))
    total_categories = Category.objects.count()
    total_tags = Tag.objects.count()
    unresolved_reports = Report.objects.filter(is_resolved=False).count()
    unread_feedback = Feedback.objects.filter(is_read=False).count()

    # Click chart data (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    click_data = (
        ClickLog.objects.filter(clicked_at__gte=thirty_days_ago)
        .annotate(date=TruncDate('clicked_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    chart_labels = [str(d['date']) for d in click_data]
    chart_values = [d['count'] for d in click_data]

    # Lists
    categories = Category.objects.annotate(
        total_links=Count('links')
    ).order_by('order', 'name')
    links = Link.objects.all().prefetch_related('categories', 'tags').order_by('-created_at')
    tags = Tag.objects.annotate(total_links=Count('links')).order_by('name')
    reports = Report.objects.all().select_related('link')[:20]
    feedbacks = Feedback.objects.all()[:20]

    # Top links
    top_links = Link.objects.filter(is_active=True).order_by('-click_count')[:10]

    # Forms
    category_form = CategoryForm()
    link_form = LinkForm()
    csv_form = CSVImportForm()

    # Handle AJAX actions
    action = request.GET.get('action', '') or request.POST.get('action', '')

    if request.method == 'POST':
        if action == 'add_category':
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, 'Category added successfully!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Error adding category.')

        elif action == 'edit_category':
            cat_id = request.POST.get('category_id')
            cat = get_object_or_404(Category, id=cat_id)
            category_form = CategoryForm(request.POST, instance=cat)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, 'Category updated!')
                return redirect('admin_dashboard')

        elif action == 'delete_category':
            cat_id = request.POST.get('category_id')
            Category.objects.filter(id=cat_id).delete()
            messages.success(request, 'Category deleted!')
            return redirect('admin_dashboard')

        elif action == 'add_link':
            link_form = LinkForm(request.POST)
            if link_form.is_valid():
                # Check duplicate
                url = link_form.cleaned_data['url']
                if Link.objects.filter(url=url).exists():
                    messages.warning(request, f'A link with URL "{url}" already exists!')
                else:
                    link_obj = link_form.save(commit=False)
                    link_obj.created_by = request.user
                    link_obj.save()
                    link_form.save_m2m()
                    # Save tags
                    tags_str = link_form.cleaned_data.get('tags_input', '')
                    tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
                    tag_objs = []
                    for name in tag_names:
                        tag, _ = Tag.objects.get_or_create(
                            name__iexact=name,
                            defaults={'name': name}
                        )
                        tag_objs.append(tag)
                    link_obj.tags.set(tag_objs)
                    messages.success(request, 'Link added successfully!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Error adding link. Check form fields.')

        elif action == 'edit_link':
            link_id = request.POST.get('link_id')
            link_obj = get_object_or_404(Link, id=link_id)
            # Save version before editing
            LinkVersion.objects.create(
                link=link_obj,
                title=link_obj.title,
                url=link_obj.url,
                description=link_obj.description,
                changed_by=request.user,
                change_note='Auto-saved before edit'
            )
            link_form = LinkForm(request.POST, instance=link_obj)
            if link_form.is_valid():
                obj = link_form.save(commit=False)
                obj.save()
                link_form.save_m2m()
                tags_str = link_form.cleaned_data.get('tags_input', '')
                tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
                tag_objs = []
                for name in tag_names:
                    tag, _ = Tag.objects.get_or_create(
                        name__iexact=name,
                        defaults={'name': name}
                    )
                    tag_objs.append(tag)
                obj.tags.set(tag_objs)
                messages.success(request, 'Link updated!')
                return redirect('admin_dashboard')

        elif action == 'delete_link':
            link_id = request.POST.get('link_id')
            Link.objects.filter(id=link_id).delete()
            messages.success(request, 'Link deleted!')
            return redirect('admin_dashboard')

        elif action == 'import_csv':
            csv_form = CSVImportForm(request.POST, request.FILES)
            if csv_form.is_valid():
                results = csv_form.process_csv(user=request.user)
                messages.success(
                    request,
                    f"Imported {results['success']} links. "
                    f"Duplicates: {results['duplicates']}. "
                    f"Errors: {len(results['errors'])}"
                )
                if results['errors']:
                    for err in results['errors'][:5]:
                        messages.warning(request, err)
                return redirect('admin_dashboard')

        elif action == 'toggle_featured':
            link_id = request.POST.get('link_id')
            link_obj = get_object_or_404(Link, id=link_id)
            link_obj.is_featured = not link_obj.is_featured
            link_obj.save(update_fields=['is_featured'])
            return JsonResponse({'featured': link_obj.is_featured})

        elif action == 'resolve_report':
            report_id = request.POST.get('report_id')
            Report.objects.filter(id=report_id).update(is_resolved=True)
            messages.success(request, 'Report resolved!')
            return redirect('admin_dashboard')

        elif action == 'mark_feedback_read':
            fb_id = request.POST.get('feedback_id')
            Feedback.objects.filter(id=fb_id).update(is_read=True)
            return redirect('admin_dashboard')

        elif action == 'delete_tag':
            tag_id = request.POST.get('tag_id')
            Tag.objects.filter(id=tag_id).delete()
            messages.success(request, 'Tag deleted!')
            return redirect('admin_dashboard')

    # For editing: fetch specific item data via AJAX
    if request.GET.get('fetch') == 'category':
        cat_id = request.GET.get('id')
        cat = get_object_or_404(Category, id=cat_id)
        return JsonResponse({
            'id': cat.id, 'name': cat.name, 'icon': cat.icon,
            'color': cat.color, 'description': cat.description,
            'order': cat.order, 'is_active': cat.is_active,
        })

    if request.GET.get('fetch') == 'link':
        link_id = request.GET.get('id')
        link_obj = get_object_or_404(Link, id=link_id)
        return JsonResponse({
            'id': link_obj.id, 'title': link_obj.title, 'url': link_obj.url,
            'description': link_obj.description,
            'categories': list(link_obj.categories.values_list('id', flat=True)),
            'tags': ', '.join(link_obj.tags.values_list('name', flat=True)),
            'is_featured': link_obj.is_featured,
            'is_active': link_obj.is_active,
        })

    context = {
        'total_links': total_links,
        'active_links': active_links,
        'broken_links': broken_links,
        'total_clicks': total_clicks,
        'total_categories': total_categories,
        'total_tags': total_tags,
        'unresolved_reports': unresolved_reports,
        'unread_feedback': unread_feedback,
        'categories': categories,
        'links': links,
        'tags': tags,
        'reports': reports,
        'feedbacks': feedbacks,
        'top_links': top_links,
        'category_form': category_form,
        'link_form': link_form,
        'csv_form': csv_form,
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
    }
    return render(request, 'core/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def export_csv(request):
    """Export all links as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="links_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Category', 'Title', 'URL', 'Description', 'Tags', 'Clicks', 'Rating', 'Status', 'Featured', 'Created'])

    for link in Link.objects.all().prefetch_related('categories', 'tags'):
        cats = ' + '.join(link.categories.values_list('name', flat=True))
        tags_str = ', '.join(link.tags.values_list('name', flat=True))
        writer.writerow([
            cats, link.title, link.url, link.description,
            tags_str, link.click_count, link.avg_rating,
            link.link_status, link.is_featured, link.created_at.strftime('%Y-%m-%d')
        ])

    return response


# ============ SITEMAPS ============

class LinkSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Link.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/service/{obj.slug}/'


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return f'/category/{obj.slug}/'