from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import TestimonialForm
from .models import Testimonial
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
@login_required
def add_edit_testimonial(request):
    # Try to get existing testimonial
    testimonial = Testimonial.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        form = TestimonialForm(request.POST, instance=testimonial)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user
            testimonial.save()
            messages.success(request, 'Your testimonial has been saved!')
            return redirect('profile', username=request.user.username)
    else:
        form = TestimonialForm(instance=testimonial)
    
    return render(request, 'main/testimonials_form.html', {'form': form})

def testimonials_list(request):
    testimonials = Testimonial.objects.filter(is_visible=True).select_related('user').order_by('-created_at')
    return render(request, 'testimonials_list.html', {'testimonials': testimonials})
