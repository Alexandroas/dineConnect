from django.shortcuts import get_object_or_404, render
from gfgauth.models import Business
from payments.models import Payment
from Restaurant_handling.decorators import business_required  
from datetime import datetime
from django.db.models import FloatField, F, Sum, Count, Window
from django.db.models import Count, Sum, FloatField
from django.db.models.functions import Cast, ExtractMonth, Rank

from reservations.models import Reservation

@business_required
def monthly_sales(request, business_id):
    current_year = datetime.now().year
    
    # Get payments for the business and aggregate by month
    monthly_payments = Payment.objects.filter(
        business_id=business_id,
        created_at__year=current_year  # Only get current year's data
    ).annotate(
        month=ExtractMonth('created_at')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    # Initialize the sales data structure
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
             'July', 'August', 'September', 'October', 'November', 'December']
    business_sales_data = [{'month': month, 'total': 0} for month in months]

    # Fill in the actual payment data
    for payment in monthly_payments:
        month_index = payment['month'] - 1  # Convert 1-based month to 0-based index
        business_sales_data[month_index]['total'] = float(payment['total'])

    # Calculate some additional statistics
    total_sales = sum(item['total'] for item in business_sales_data)
    average_monthly_sales = total_sales / 12 if total_sales > 0 else 0
    
    context = {
        'business_sales_data': business_sales_data,
        'total_sales': total_sales,
        'average_monthly_sales': average_monthly_sales,
        'current_year': current_year
    }
    
    return render(request, 'graphs/monthly_sales.html', context)

@business_required
def analytics(request, business_id):
    business = get_object_or_404(Business, business_id=business_id)
    return render(request, 'graphs/analytics.html', {'business': business})

@business_required
def montly_reservations(request, business_id):
    current_year = datetime.now().year
    montly_reservations = Reservation.objects.filter(
        business_id=business_id,
        reservation_date__year=current_year,
        # Only count confirmed or completed reservations
        reservation_status__in=['Confirmed', 'Completed']
    ).annotate(
        month=ExtractMonth('reservation_date')
    ).values('month').annotate(
        total=Sum('reservation_party_size')
    ).order_by('month')

    months = ['January', 'February', 'March', 'April', 'May', 'June', 
             'July', 'August', 'September', 'October', 'November', 'December']
    business_reservations_data = [{'month': month, 'total': 0} for month in months]
    
    for reservation in montly_reservations:
        month_index = reservation['month'] - 1
        business_reservations_data[month_index]['total'] = float(reservation['total'])
    
    total_reservations = sum(item['total'] for item in business_reservations_data)
    average_monthly_reservations = total_reservations / 12 if total_reservations > 0 else 0
    
    context = {
        'business_reservations_data': business_reservations_data,
        'total_reservations': total_reservations,
        'average_monthly_reservations': average_monthly_reservations,
        'current_year': current_year
    }
    return render(request, 'graphs/monthly_reservations.html', context)


@business_required
def dish_popularity(request, business_id):
    current_year = datetime.now().year
   
    # Get most popular dishes by total reservations
    dish_popularity = Reservation.objects.filter(
        business_id=business_id,
        reservation_date__year=current_year,
        reservation_status='Completed'
    ).values(
        'dish_id__dish_name',
        'dish_id__dish_cost'
    ).annotate(
        total_orders=Count('reservation_id'),
        avg_party_size=Sum('reservation_party_size') / Cast(Count('reservation_id'), FloatField())
    ).order_by('-total_orders')[:10]

    # Get monthly trends
    monthly_trends = Reservation.objects.filter(
        business_id=business_id,
        reservation_date__year=current_year,
        reservation_status='Completed'
    ).annotate(
        month=ExtractMonth('reservation_date')
    ).values('month').annotate(
        total_orders=Count('reservation_id'),
    ).order_by('month')

    # Prepare monthly data
    months = ['January', 'February', 'March', 'April', 'May', 'June',
             'July', 'August', 'September', 'October', 'November', 'December']
   
    # Calculate overall statistics - safely handle None values
    total_orders = sum(dish['total_orders'] or 0 for dish in dish_popularity)

    # Format the data for the charts
    chart_data = {
        'labels': [dish['dish_id__dish_name'] for dish in dish_popularity],
        'orders': [dish['total_orders'] or 0 for dish in dish_popularity],
    }
   
    context = {
        'dish_popularity': dish_popularity,
        'monthly_trends': monthly_trends,
        'months': months,
        'total_orders': total_orders,
        'current_year': current_year,
        'chart_data': chart_data
    }
    return render(request, 'graphs/dish_popularity.html', context)