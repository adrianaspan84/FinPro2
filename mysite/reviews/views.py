from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView, UpdateView
from django.db.models import Count, Avg

from main.models import Profile
from .forms import ReviewForm
from .models import Review


def _review_list_context(form=None):
    reviews = Review.objects.select_related('user').filter(is_approved=True)

    stats = Review.objects.filter(is_approved=True).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    total = stats['total_reviews'] or 0
    rating_rows = []
    for rating in range(1, 6):
        count = Review.objects.filter(is_approved=True, rating=rating).count()
        percentage = (count * 100 // total) if total > 0 else 0
        rating_rows.append({
            'rating': rating,
            'count': count,
            'percentage': percentage
        })
    rating_rows.reverse()

    return {
        'reviews': reviews,
        'form': form,
        'avg_rating': stats['avg_rating'] or 0,
        'total_reviews': total,
        'rating_rows': rating_rows,
    }


def review_list(request):
    form = ReviewForm() if request.user.is_authenticated else None
    context = _review_list_context(form=form)
    return render(request, 'reviews/review_list.html', context)


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    success_url = reverse_lazy('reviews_list')

    def get(self, request, *args, **kwargs):
        return redirect('reviews_list')

    def post(self, request, *args, **kwargs):
        profile, _created = Profile.objects.get_or_create(user=request.user)
        if profile.role != 'client' and not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, _('Atsiliepimus gali rašyti tik klientai.'))
            return redirect('reviews_list')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_approved = True
        response = super().form_valid(form)
        messages.success(self.request, _('Atsiliepimas išsaugotas.'))
        return response

    def form_invalid(self, form):
        messages.error(self.request, _('Nepavyko išsaugoti atsiliepimo. Patikrinkite laukus.'))
        context = _review_list_context(form=form)
        return render(self.request, 'reviews/review_list.html', context, status=400)


class StaffOrSuperuserRequiredMixin(UserPassesTestMixin):
    error_message = _('Neturite teisės redaguoti šio atsiliepimo.')

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, self.error_message)
            return redirect('reviews_list')
        return super().handle_no_permission()


class ReviewUpdateView(LoginRequiredMixin, StaffOrSuperuserRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    pk_url_kwarg = 'review_id'
    template_name = 'reviews/review_form.html'
    success_url = reverse_lazy('reviews_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Atsiliepimas atnaujintas.'))
        return response


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    pk_url_kwarg = 'review_id'
    success_url = reverse_lazy('reviews_list')

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, _('Neturite teisės trinti šio atsiliepimo.'))
            return redirect('reviews_list')
        return super().handle_no_permission()

    def get(self, request, *args, **kwargs):
        return redirect('reviews_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, _('Atsiliepimas ištrintas.'))
        return HttpResponseRedirect(self.get_success_url())
