import requests
from django.conf import settings


def create_checkout_session(course):
    """
    Создает продукт, цену и сессию оплаты в Stripe для заданного курса.
    Возвращает словарь с ID и ссылкой на оплату.
    """
    headers = {
        "Authorization": f"Bearer {settings.STRIPE_SECRET_KEY}",
    }

    # 1. Создаем продукт
    product_data = {
        "name": course.title,
        "description": course.description or "",
    }
    product_response = requests.post(
        f"{settings.STRIPE_BASE_URL}/products", json=product_data, headers=headers
    )
    if product_response.status_code != 200:
        raise Exception(f"Stripe product creation failed: {product_response.json()}")
    product_id = product_response.json()["id"]

    # 2. Создаем цену (в копейках!)
    price_data = {
        "product": product_id,
        "unit_amount": int((course.price or 0) * 100),
        "currency": "rub",
    }
    price_response = requests.post(
        f"{settings.STRIPE_BASE_URL}/prices", json=price_data, headers=headers
    )
    if price_response.status_code != 200:
        raise Exception(f"Stripe price creation failed: {price_response.json()}")
    price_id = price_response.json()["id"]

    # 3. Создаем сессию checkout
    session_data = {
        "line_items": [{"price": price_id, "quantity": 1}],
        "mode": "payment",
        "success_url": "http://example.com/success",
        "cancel_url": "http://example.com/cancel",
    }
    session_response = requests.post(
        f"{settings.STRIPE_BASE_URL}/checkout/sessions",
        json=session_data,
        headers=headers,
    )
    if session_response.status_code != 200:
        raise Exception(f"Stripe session creation failed: {session_response.json()}")
    session = session_response.json()

    return {
        "stripe_product_id": product_id,
        "stripe_price_id": price_id,
        "stripe_session_id": session["id"],
        "payment_url": session["url"],
    }
