from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Review
from .forms import ReviewForm
from profiles.models import Profile, MatchResponse


def user_is_matched(user1, user2):
    """
    Returns True if user1 and user2 have liked each other.
    """
    try:
        profile2 = user2.profile  # user2's profile
        liked_by_user1 = MatchResponse.objects.filter(
            from_user=user1,
            to_profile=profile2,
            liked=True
        ).exists()

        profile1 = user1.profile
        liked_by_user2 = MatchResponse.objects.filter(
            from_user=user2,
            to_profile=profile1,
            liked=True
        ).exists()

        return liked_by_user1 and liked_by_user2

    except Profile.DoesNotExist:
        return False


@login_required
def leave_review(request, user_id):
    reviewee = get_object_or_404(User, id=user_id)

    if request.user == reviewee:
        messages.error(request, "You cannot review yourself.")
        return redirect('view_profile', user_id=reviewee.id)

    if not user_is_matched(request.user, reviewee):
        messages.error(request, "You can only review matched users.")
        return redirect('view_profile', user_id=reviewee.id)

    existing_review = Review.objects.filter(
        reviewer=request.user, reviewee=reviewee).first()
    form = ReviewForm(instance=existing_review)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewee = reviewee
            review.save()
            messages.success(request, "Review submitted successfully.")
            return redirect('view_profile', user_id=reviewee.id)

    return render(request, 'reviews/leave_review.html', {
        'form': form,
        'reviewee': reviewee,
        'existing_review': existing_review,
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    form = ReviewForm(request.POST or None, instance=review)
    if form.is_valid():
        form.save()
        return redirect('profile_detail', profile_id=review.profile.id)
    return render(request, 'reviews/edit_review.html', {'form': form})


@login_required
def delete_review(request, user_id):
    review = get_object_or_404(
        Review, reviewer=request.user, reviewee__id=user_id)
    review.delete()
    messages.success(request, "Your review has been deleted.")
    return redirect('view_profile', user_id=user_id)
