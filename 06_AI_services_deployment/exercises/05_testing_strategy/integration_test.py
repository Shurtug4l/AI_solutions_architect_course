
def get_product_price(product_id):
    # Simulated product database
    product_database = {
        1: 100.0,  # Price for product ID 1
        2: 200.0,  # Price for product ID 2
        3: 50.0    # Price for product ID 3
    }
    return product_database.get(product_id, 0.0)  # Returns 0.0 if the product is not found

def calculate_cart_total(product_ids):
    # Compute the cart total
    total = 0.0
    for product_id in product_ids:
        total += get_product_price(product_id)
    return total

def test_calculate_cart_total():
    # Test case: total for a cart with several products
    cart = [1, 2, 3]  # Product ids in the cart
    expected_total = 350.0  # Expected total (100 + 200 + 50)

    # Compute the total with calculate_cart_total
    actual_total = calculate_cart_total(cart)

    # Check the computed total matches the expected one
    assert actual_total == expected_total, f"Expected {expected_total}, but got {actual_total}"
