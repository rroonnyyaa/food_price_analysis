import pandas as pd
import numpy as np
from datetime import timedelta, date, datetime # Added datetime import
from sklearn.linear_model import LinearRegression
from .models import PriceRecord

def get_price_forecast(product_id, days_ahead=30):
    """
    Predicts price for the next 'days_ahead' days using linear regression.
    Returns a dictionary with model status, score, predicted price, and trend.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=90) # Use 90 days for better trend
    
    records = PriceRecord.objects.filter(
        product_id=product_id,
        date_recorded__gte=start_date
    ).order_by('date_recorded')
    
    if records.count() < 5:
        return {'model_status': 'insufficient_data'}

    df = pd.DataFrame(list(records.values('date_recorded', 'price')))
    df['date_ordinal'] = pd.to_datetime(df['date_recorded']).apply(lambda x: x.toordinal())
    
    X = df[['date_ordinal']]
    y = df['price']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate R^2 score
    r2 = model.score(X, y)
    
    # Predict for today + days_ahead
    future_date = end_date + timedelta(days=days_ahead)
    future_ordinal = np.array([[future_date.toordinal()]])
    predicted_future_price = model.predict(future_ordinal)[0]
    
    # Predict for today (to calculate trend slope)
    today_ordinal = np.array([[end_date.toordinal()]])
    predicted_today_price = model.predict(today_ordinal)[0]
    
    trend_total = predicted_future_price - predicted_today_price
    trend_daily = trend_total / days_ahead
    
    return {
        'model_status': 'success',
        'r2_score': round(r2, 2),
        'predicted_price': round(float(predicted_future_price), 2),
        'trend': round(float(trend_daily), 2), # Daily change in Rubles
        'dates': [], # Can define if needed for chart
        'prices': []
    }

def get_market_inflation(days=30):
    """
    Calculates the average price of the entire product basket over time.
    """
    stop_date = date.today()
    start_date = stop_date - timedelta(days=days)
    
    records = PriceRecord.objects.filter(
        date_recorded__gte=start_date
    ).values('date_recorded', 'price')
    
    df = pd.DataFrame(records)
    if df.empty:
        return {'dates': [], 'prices': [], 'change': 0}
        
    # Ensure price is numeric (float) to avoid TypeError with Decimal objects
    df['price'] = df['price'].astype(float)

    # Group by date and mean
    daily_avg = df.groupby('date_recorded')['price'].mean().reset_index()
    daily_avg = daily_avg.sort_values('date_recorded')
    
    dates = daily_avg['date_recorded'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()
    prices = daily_avg['price'].round(2).tolist()
    
    inflation_change = 0
    if len(prices) > 1:
        inflation_change = ((prices[-1] - prices[0]) / prices[0]) * 100
        
    return {
        'dates': dates,
        'prices': prices,
        'change': round(inflation_change, 2)
    }
