import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv


def get_database() -> pymongo.database.Database:
    """
    Connects to MongoDB Cloud and returns the database object.

    Returns:
        pymongo.database.Database: The database object for the inventory management system.
    """
    load_dotenv()
    connection_string = os.getenv('mongodb_key')
    client = MongoClient(connection_string)
    imsDB = client['inventoryManagementSystemDB']
    return imsDB


def add_product(db: pymongo.database.Database, name: str, quantity: int, price: float) -> None:
    """
    Adds a product to the inventory.

    Args:
        db (pymongo.database.Database): The database object.
        name (str): The name of the product.
        quantity (int): The quantity of the product.
        price (float): The price of the product.
    """
    product = {"name": name, "quantity": quantity, "price": price}
    db['product'].insert_one(product)
    print("Product added!")


def delete_product(db: pymongo.database.Database, name: str) -> None:
    """
    Deletes a product from the inventory.

    Args:
        db (pymongo.database.Database): The database object.
        name (str): The name of the product to delete.
    """
    product = {"name": name}
    db['product'].delete_one(product)
    print("Product deleted!")


def display_product(db: pymongo.database.Database) -> None:
    """
    Displays all products in the inventory.

    Args:
        db (pymongo.database.Database): The database object.
    """
    print("Current products in your inventory:")
    for index, product in enumerate(db['product'].find(), start=1):
        print(f"{index}. Product Name: {product['name']} \nQuantity: {product['quantity']} \nPrice: {product['price']}")


def search_product(db: pymongo.database.Database, name: str) -> None:
    """
    Searches for a product in the inventory.

    Args:
        db (pymongo.database.Database): The database object.
        name (str): The name of the product to search for.
    """
    regEx = name + "*"  # Regular expression allows non-full-name search
    query = {"name": {"$regex": regEx, "$options": "i"}}  # Options 'i' allow case-insensitive search
    result = db['product'].find(query)

    result_found = False
    for index, product in enumerate(result, start=1):
        print(f"{index}. Product Name: {product['name']} \nQuantity: {product['quantity']} \nPrice: {product['price']}")
        result_found = True

    if not result_found:
        print("Product not found")


def update_quantity(db: pymongo.database.Database, name: str, new_quantity: int) -> None:
    """
    Updates the quantity of a product in the inventory.

    Args:
        db (pymongo.database.Database): The database object.
        name (str): The name of the product.
        new_quantity (int): The new quantity for the product.
    """
    query = {"name": {"$regex": name, "$options": "i"}}
    result = db['product'].find(query)

    result_found = False
    for product in result:
        result_found = True

    if result_found:
        update = {"$set": {"quantity": new_quantity}}
        db['product'].update_one(query, update)
        print("Quantity updated!")
    else:
        print("Product not found")


def generate_report(db: pymongo.database.Database) -> None:
    """
    Generates a report with total quantity and inventory value.

    Args:
        db (pymongo.database.Database): The database object.
    """
    total_quantity_pipeline = [
        {
            '$group': {
                '_id': None,
                'total_quantity': {'$sum': '$quantity'}
            }
        }
    ]
    results = db['product'].aggregate(total_quantity_pipeline)
    for result in results:
        print("Total quantity: ", result['total_quantity'])

    total_inventory_value_pipeline = [
        {
            '$group': {
                '_id': None,
                'total_inventory_value': {"$sum": {'$multiply': ['$quantity', '$price']}}
            }
        }
    ]
    results = db['product'].aggregate(total_inventory_value_pipeline)
    for result in results:
        print("Total inventory value: ", result['total_inventory_value'])


def show_low_stock_products(db: pymongo.database.Database, threshold: int) -> None:
    """
    Displays products with quantities below a specified threshold.

    Args:
        db (pymongo.database.Database): The database object.
        threshold (int): The stock threshold.
    """
    query = {"quantity": {"$lte": threshold}}
    result = db['product'].find(query)
    for index, product in enumerate(result, start=1):
        print(f"{index}. Product Name: {product['name']} \nQuantity: {product['quantity']} \nPrice: {product['price']}")
                                                                                                     


def main()-> None:
    """Main function for user interaction."""
    while True:
        db = get_database()
        print("\nWelcome to the Inventory Management System!")
        print("1. Add a product")
        print("2. Delete a product")
        print("3. Display All products")
        print("4. Search for a product")
        print("5. Update the quantity of a product")
        print("6. Genearate a report")
        print("7. Show Low Stock Products")
        print("8. Exit")

        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            name = input("Enter a product name to add: ")
            quantity = input("Enter the quantity's name: ")
            price = input("Enter the price: ")
            add_product(db, name, int(quantity), int(price))
        elif choice == '2':
            name = input("Enter a product name to delete: ")
            delete_product(db, name)
        elif choice == '3':
            display_product(db)
        elif choice == '4':
            name = input("Enter a product name to search: ")
            search_product(db, name)
        elif choice == '5':
            name = input("Enter a the product name: ")
            new_quantity = input("Enter the new quantity: ")
            update_quantity(db, name, int(new_quantity))
        elif choice == '6':
            generate_report(db)
        elif choice == '7':
            threshold = input("Specified a stock threshold: ")
            show_low_stock_products(db, int(threshold))
        elif choice == '8':
            print("Exiting the Inventory Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()