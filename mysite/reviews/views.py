from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from main.models import Profile
from .forms import ReviewForm
from .models import Review


def review_list(request):
    reviews = Review.objects.select_related('user').filter(is_approved=True)
    form = ReviewForm() if request.user.is_authenticated else None
    return render(request, 'reviews/review_list.html', {'reviews': reviews, 'form': form})


@login_required
def review_create(request):
    if request.method != 'POST':
        return redirect('reviews_list')

    profile, _ = Profile.objects.get_or_create(user=request.user)
    if profile.role != 'client' and not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, _('Atsiliepimus gali rašyti tik klientai.'))
        return redirect('reviews_list')

    form = ReviewForm(request.POST, request.FILES)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.is_approved = True
        review.save()
        messages.success(request, _('Atsiliepimas išsaugotas.'))
    else:
        messages.error(request, _('Nepavyko išsaugoti atsiliepimo. Patikrinkite laukus.'))

    return redirect('reviews_list')


@login_required
def review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, _('Neturite teisės redaguoti šio atsiliepimo.'))
        return redirect('reviews_list')

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, _('Atsiliepimas atnaujintas.'))
            return redirect('reviews_list')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/review_form.html', {'form': form, 'review': review})


@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, _('Neturite teisės trinti šio atsiliepimo.'))
        return redirect('reviews_list')

    if request.method == 'POST':
        review.delete()
        messages.success(request, _('Atsiliepimas ištrintas.'))

    return redirect('reviews_list')
