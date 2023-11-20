from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ProductPagination(PageNumberPagination):
    page_size = 1
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response(
            {
                "link": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "result": data,
            }
        )


def update_product_quantity(product_in_cart, product, request_data_quantity):
    product.quantity += product_in_cart.quantity - request_data_quantity
    return product.save()


def get_star():
    return [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")]


CART_ADD_PRODUCT_PATH = "add"
CART_DELETE_PRODUCT_PATH = "delete"
CART_CHANGE_PRODUCT_QUANTITY_IN_CART_PATH = "update"
CHECKOUT_PATH = "/checkout/"


def test_function():
    pass
