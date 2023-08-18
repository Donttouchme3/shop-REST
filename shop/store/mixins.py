from .models import Order


def create_order(user, shipping, cart_product, 
                 total_price, total_quantity, session_id):
    order = Order.objects.create(user=user,
                         shipping=shipping,
                         order_total_price=total_price,
                         order_product_total_quantity=total_quantity,
                         session_id=session_id)
    order.cart_product.set(cart_product)
    
    return order


CART_ADD_PRODUCT_PATH = '/api/cart/add/'
CART_DELETE_PRODUCT_PATH = '/api/cart/delete/'
CHECKOUT_PATH = '/checkout/'
