import random
import pandas as pd
from datetime import datetime

#cat . subcat with merchants and items ex
categories = {
    "Food & Drinks": {
        "Restaurants": {
            "Domino's Pizza": ["Margherita Pizza", "Farmhouse Pizza", "Garlic Bread", "Coke"],
            "Haldiram's": ["Samosa", "Paneer Tikka", "Bhujia", "Jalebi"],
            "Barbeque Nation": ["Grilled Chicken", "Veg Platter", "Fish Tikka"],
            "McDonald's": ["Burger", "Fries", "Coke", "McFlurry"],
            "KFC": ["Fried Chicken", "Masala Wings", "Burger", "Fries"]
        },
        "Coffee Shops": {
            "Café Coffee Day": ["Cappuccino", "Espresso", "Latte", "Cold Coffee"],
            "Starbucks India": ["Frappuccino", "Americano", "Caramel Macchiato"],
            "Chai Point": ["Masala Chai", "Green Tea", "Iced Tea"]
        },
        "Groceries": {
            "Big Bazaar": ["Rice", "Atta", "Sugar", "Milk", "Bread", "Biscuits"],
            "DMart": ["Vegetables", "Eggs", "Oil", "Salt", "Spices", "Flour", "Soap"],
            "Reliance Fresh": ["Milk", "Curd", "Vegetables", "Fruits", "Bread"]
        },
        "Food Delivery": {
            "Swiggy": ["Pizza", "Burger", "Sandwich", "Thali", "Ice Cream"],
            "Zomato": ["Pizza", "Biryani", "Pasta", "Desserts"]
        }
    },
    "Shopping": {
        "Online": {
            "Amazon India": ["Mobile Phone", "Laptop", "Headphones", "Books", "Watch"],
            "Flipkart": ["Clothing", "Shoes", "Electronics", "Accessories"],
            "Myntra": ["T-Shirts", "Jeans", "Dresses", "Footwear"]
        },
        "Clothing": {
            "Pantaloons": ["Shirt", "Jeans", "Kurta", "T-Shirt"],
            "Westside": ["Dress", "Skirt", "Blouse"],
            "FabIndia": ["Kurta", "Shawl", "Ethnic Wear"]
        },
        "Electronics": {
            "Croma": ["Smartphone", "Laptop", "Headphones", "TV"],
            "Reliance Digital": ["Smartphone", "Tablet", "Camera"]
        },
        "Departmental Stores": {
            "BigBasket": ["Milk", "Rice", "Oil", "Spices"],
            "DMart Ready": ["Snacks", "Detergent", "Juice"]
        }
    },
    "Bills & Utilities": {
        "Electricity": {"BSES Rajdhani": ["Electricity Bill"]},
        "Water": {"BWSSB": ["Water Bill"]},
        "Gas": {"Indane": ["Gas Cylinder"]},
        "Mobile/Internet": {"Jio": ["Mobile Recharge", "Internet Bill"], "Airtel": ["Mobile Recharge", "Internet Bill"]},
        "DTH": {"Tata Play": ["DTH Recharge"]}
    },
    "Travel": {
        "Flights": {"IndiGo": ["Flight Ticket"], "Air India": ["Flight Ticket"]},
        "Trains & Bus": {"IRCTC": ["Train Ticket"], "RedBus": ["Bus Ticket"]},
        "Hotels": {"OYO": ["Room Booking"], "Taj Hotels": ["Room Booking"]},
        "Fuel": {"IndianOil": ["Petrol", "Diesel"]}
    },
    "Transport": {
        "Taxi/Ride-hailing": {"Ola": ["Cab Fare"], "Uber India": ["Cab Fare"]},
        "Public Transit": {"Delhi Metro": ["Metro Ticket"], "Mumbai Metro": ["Metro Ticket"]}
    },
    "Health & Fitness": {
        "Pharmacy": {"Apollo Pharmacy": ["Paracetamol", "Vitamins", "Cough Syrup"]},
        "Gyms": {"Cult.Fit": ["Gym Membership", "Personal Training"]}
    },
    "Entertainment": {
        "Cinema": {"PVR Cinemas": ["Movie Ticket"], "INOX": ["Movie Ticket"]},
        "Streaming": {"Netflix India": ["Subscription"], "Hotstar": ["Subscription"]}
    },
    "Education": {
        "Online Courses": {"Byju's": ["Math Course", "Science Course"], "Unacademy": ["Video Subscription"]},
        "Books & Stationery": {"Sapna Book House": ["Notebook", "Pen", "Book"]}
    },
    "Miscellaneous": {
        "Gifts": {"Ferns N Petals": ["Flower Bouquet", "Gift Hamper"]},
        "Charities": {"Akshaya Patra": ["Donation"]},
        "Pet Stores": {"Heads Up For Tails": ["Dog Food", "Cat Food"]}
    }
}

def random_date():
    start = datetime(2020,1,1)
    end = datetime(2025,12,31)
    return (start + (end-start) * random.random()).strftime("%m/%d/%Y")

def random_invoice_number():
    return str(random.randint(10000,99999))

def random_amount():
    return random.randint(50,5000)


def generate_dataset(n):
    rows = []
    for _ in range(n):
        category = random.choice(list(categories.keys()))
        subcategory = random.choice(list(categories[category].keys()))
        merchant = random.choice(list(categories[category][subcategory].keys()))
        items_list = categories[category][subcategory][merchant]

        style = random.choices(
            ["minimal", "medium", "full"], 
            weights=[0.4, 0.4, 0.2], k=1
        )[0]

        #some desc variation for different receipts invoice types
        if style == "minimal":
            description = f"{merchant} {random.choice(items_list)} ₹{random_amount()}"
        
        elif style == "medium":
            description = (
                f"{random.choice(['Purchase', 'Payment', 'Transaction'])} at {merchant}, "
                f"Item: {random.choice(items_list)}, Qty: {random.randint(1,5)}, "
                f"Total: ₹{random_amount()}, Date: {random_date()}"
            )
        else:
            n_items = min(len(items_list), random.randint(2, 3))
            items_str = ", ".join(random.sample(items_list, n_items))
            description = (
                f"Invoice #{random_invoice_number()} | Merchant: {merchant} | Date: {random_date()} | "
                f"Items: {items_str} | Qty: {random.randint(1,5)} | "
                f"Price: ₹{random_amount()} | Tax: ₹{random.randint(10,200)} | Total: ₹{random_amount()}"
            )

        rows.append([description, category, subcategory, merchant, ", ".join(items_list)])

    df = pd.DataFrame(rows, columns=["Description", "Category", "Subcategory", "Merchant", "Items"])
    return df

df = generate_dataset(5000)
df.to_csv("expense_dataset.csv" , index=False)
print(df.head(10));


