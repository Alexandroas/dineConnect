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
    """
    View function to display the monthly sales data for a given business.
    Args:
        request (HttpRequest): The HTTP request object.
        business_id (int): The ID of the business for which to retrieve sales data.
    Returns:
        HttpResponse: The rendered HTML page displaying the monthly sales data.
    The function performs the following steps:
    1. Retrieves the current year.
    2. Queries the Payment model to get payments for the specified business, filtered by the current year.
    3. Aggregates the payments by month and calculates the total amount for each month.
    4. Initializes a data structure to hold sales data for each month of the year.
    5. Fills in the actual payment data into the initialized data structure.
    6. Calculates additional statistics such as total sales and average monthly sales.
    7. Prepares the context dictionary with the sales data and statistics.
    8. Renders the 'graphs/monthly_sales.html' template with the context data.
    """
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
    """
    View to display monthly reservations for a business.
    This view calculates the total number of reservations per month for the current year,
    only considering reservations that are either confirmed or completed. It then prepares
    the data to be displayed in a template.
    Args:
        request (HttpRequest): The HTTP request object.
        business_id (int): The ID of the business for which to display reservations.
    Returns:
        HttpResponse: The rendered HTML page displaying the monthly reservations data.
    Context:
        business_reservations_data (list): A list of dictionaries containing the month and total reservations.
        total_reservations (float): The total number of reservations for the current year.
        average_monthly_reservations (float): The average number of reservations per month.
        current_year (int): The current year.
    """
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
    """
    View to display the popularity of dishes for a specific business within the current year.
    This view calculates and displays the most popular dishes based on the total number of reservations
    and the average party size for each dish. It also provides monthly trends of reservations.
    Args:
        request (HttpRequest): The HTTP request object.
        business_id (int): The ID of the business for which to display dish popularity.
    Returns:
        HttpResponse: The rendered HTML page displaying dish popularity and monthly trends.
    Context:
        dish_popularity (QuerySet): A queryset containing the most popular dishes with their names, costs,
                                    total orders, and average party sizes.
        monthly_trends (QuerySet): A queryset containing the monthly trends of reservations.
        months (list): A list of month names for display purposes.
        total_orders (int): The total number of orders for the most popular dishes.
        current_year (int): The current year.
        chart_data (dict): A dictionary containing labels and orders for chart visualization.
    """
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