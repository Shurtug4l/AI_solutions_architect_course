
def get_product_price(product_id):
    # Simulazione di un database di prodotti
    product_database = {
        1: 100.0,  # Prezzo per il prodotto con ID 1
        2: 200.0,  # Prezzo per il prodotto con ID 2
        3: 50.0    # Prezzo per il prodotto con ID 3
    }
    return product_database.get(product_id, 0.0)  # Ritorna 0.0 se il prodotto non è trovato

def calculate_cart_total(product_ids):
    # Calcola il totale del carrello
    total = 0.0
    for product_id in product_ids:
        total += get_product_price(product_id)
    return total

def test_calculate_cart_total():
    # Caso di test: calcolo del totale per un carrello con più prodotti
    cart = [1, 2, 3]  # ID dei prodotti nel carrello
    expected_total = 350.0  # Totale atteso (100 + 200 + 50)
    
    # Calcola il totale usando la funzione calculate_cart_total
    actual_total = calculate_cart_total(cart)
    
    # Verifica se il totale calcolato corrisponde al totale atteso
    assert actual_total == expected_total, f"Expected {expected_total}, but got {actual_total}"
