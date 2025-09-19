import random
import pandas as pd
from datetime import datetime

#cat . subcat with merchants and items ex
categories = {
  "Food & Drinks": {
    "Restaurants": {
      "Domino's Pizza": ["Margherita Pizza", "Farmhouse Pizza", "Garlic Bread", "Pepsi/Coke"],
      "Haldiram's": ["Samosa", "Paneer Tikka", "Bhujia", "Jalebi"],
      "Barbeque Nation": ["Grilled Chicken", "Veg Platter", "Fish Tikka"],
      "McDonald's": ["Burger", "Fries", "McNuggets", "McFlurry"],
      "KFC": ["Fried Chicken", "Masala Wings", "Masala Fries"],
      "Biryani By Kilo": ["Chicken Biryani", "Vegetable Biryani", "Raita"],
      "Saravana Bhavan": ["Idli", "Dosa", "Sambar", "Vada"],
      "Local Restaurant": ["Thali", "Curry Plate", "Chapati"]
    },
    "Coffee Shops": {
      "Starbucks India": ["Cappuccino", "Latte", "Americano", "Frappuccino"],
      "Café Coffee Day": ["Filter Coffee", "Ice Coffee", "Sandwich"],
      "Chai Point": ["Masala Chai", "Ginger Tea", "Iced Tea"],
      "Third Wave Coffee": ["Cold Brew", "Espresso", "Flat White"]
    },
    "Bakeries & Quick Eats": {
      "Theobroma": ["Brownie", "Coffee Cake", "Pastry"],
      "Local Bakery": ["Bread Loaf", "Cookies", "Muffin"],
      "Haldiram's Sweets & Snacks": ["Sweets Box", "Namkeen Pack"]
    },
    "Food Delivery": {
      "Swiggy": ["Pizza Delivery", "Biryani Delivery", "Meal Combo"],
      "Zomato": ["Restaurant Delivery", "Desserts", "Combo Meal"],
      "Dunzo Food": ["Quick Grocery Delivery", "Tiffin"]
    }
  },

  "Groceries": {
    "Supermarkets (Offline)": {
      "DMart": ["Rice 5kg", "Wheat Flour 5kg", "Refined Oil 1L", "Toothpaste", "Detergent"],
      "Big Bazaar": ["Biscuits", "Milk Pack", "Packaged Snacks", "Cooking Oil", "Soaps"],
      "Reliance Fresh": ["Fresh Vegetables", "Fruits Pack", "Dairy Milk", "Curd"],
      "More Supermarket": ["Pulses", "Spices", "Bread", "Eggs"]
    },
    "Online Grocers / Quick Commerce": {
      "BigBasket": ["Fresh Vegetables", "Fruits", "Staples (Rice/Atta)", "Dairy"],
      "Blinkit": ["Milk 1L", "Bread Loaf", "Instant Noodles", "Eggs (6)"],
      "JioMart": ["Staples", "Cooking Oil", "Packaged Foods"],
      "Amazon Pantry": ["Packaged Snacks", "Biscuits", "Tea Powder"]
    },
    "Specialty / Gourmet": {
      "Nature's Basket": ["Imported Cheese", "Olive Oil", "Organic Quinoa", "Gourmet Chocolate"],
      "Foodhall": ["Specialty Coffee", "Artisanal Cheese", "Imported Sausages"]
    },
    "Local Kirana / Corner Store": {
      "Local Kirana Store": ["Milk 1L", "Bread", "Sugar 1kg", "Salt 1kg", "Tea Powder"],
      "Neighborhood Kirana": ["Matchbox", "Chocolates", "Instant Coffee", "Packaged Snacks"]
    }
  },

  "Shopping": {
    "Online Marketplaces": {
      "Amazon India": ["Mobile Phone", "Laptop", "Headphones", "Books", "Watch"],
      "Flipkart": ["Clothing", "Shoes", "Electronics", "Accessories"],
      "Myntra": ["T-Shirts", "Jeans", "Dresses", "Footwear"],
      "Nykaa": ["Makeup", "Skincare", "Perfume"]
    },
    "Clothing & Apparel": {
      "Pantaloons": ["Shirt", "Kurta", "Trousers", "Kids Wear"],
      "Westside": ["Dress", "Jacket", "Saree", "Blouse"],
      "FabIndia": ["Kurta", "Handloom Shawl", "Ethnic Wear"]
    },
    "Electronics & Gadgets": {
      "Croma": ["Smartphone", "LED TV", "Laptop", "Bluetooth Speaker"],
      "Reliance Digital": ["Washing Machine", "AC", "Camera"]
    },
    "Furniture & Home": {
      "Pepperfry": ["Sofa", "Dining Table", "Chair"],
      "Urban Ladder": ["Bed", "TV Unit", "Bookshelf"],
      "IKEA India": ["Wardrobe", "Kitchen Rack", "Study Table"]
    }
  },

  "Bills & Utilities": {
    "Electricity": {
      "BSES Rajdhani": ["Electricity Bill Payment"],
      "Tata Power Delhi": ["Electricity Bill"]
    },
    "Water Bill": {
      "BWSSB": ["Water Bill Payment"],
      "Delhi Jal Board": ["Water Bill"]
    },
    "Gas": {
      "Indane": ["Gas Cylinder Refill"],
      "HP Gas": ["Gas Cylinder Booking"]
    },
    "Mobile & Internet": {
      "Jio": ["Prepaid Recharge", "Postpaid Bill", "Broadband Bill"],
      "Airtel": ["Recharge", "Broadband Bill"],
      "Vi": ["Mobile Recharge"]
    },
    "DTH": {
      "Tata Play": ["DTH Recharge"],
      "DishTV": ["DTH Recharge"]
    }
  },

  "Travel": {
    "Flights": {
      "IndiGo": ["Flight Ticket Domestic", "Domestic Cancellation Fee"],
      "Vistara": ["Flight Ticket"]
    },
    "Trains & Bus": {
      "IRCTC": ["Train Ticket AC3", "Tatkal Booking"],
      "RedBus": ["Bus Ticket", "Seat Reservation"]
    },
    "Hotels & Stays": {
      "OYO": ["Room Booking", "Weekend Stay"],
      "Taj Hotels": ["Suite Booking", "Room Service"]
    },
    "Fuel & Petrol Pumps": {
      "IndianOil": ["Petrol Full Tank", "Diesel Full Tank"],
      "Bharat Petroleum": ["Petrol", "Lubricant"]
    },
    "Travel Agents / Aggregators": {
      "MakeMyTrip": ["Flight Booking", "Hotel Booking"],
      "Yatra": ["Holiday Package"]
    }
  },

  "Transport": {
    "Ride-hailing": {
      "Ola": ["Cab Ride", "Auto Ride"],
      "Uber India": ["Cab Ride", "Airport Drop"],
      "Rapido": ["Bike Ride"]
    },
    "Public Transit": {
      "Delhi Metro": ["Token", "Smart Card Recharge"],
      "Mumbai Local": ["Train Ticket"]
    },
    "Vehicle Services & Repairs": {
      "Maruti Service": ["Car Service", "Oil Change"],
      "Bosch Car Service": ["Engine Check", "Wheel Alignment"]
    }
  },

  "Entertainment": {
    "Cinema": {
      "PVR Cinemas": ["Movie Ticket", "Combo"],
      "INOX": ["Movie Ticket"]
    },
    "Streaming / Subscriptions": {
      "Amazon Prime Video": ["Monthly Subscription"],
      "Hotstar (Disney+)": ["Subscription"],
      "Netflix India": ["Monthly Plan"]
    },
    "Events & Tickets": {
      "BookMyShow": ["Concert Ticket", "Event Ticket"],
      "Paytm Insider": ["Event Booking"]
    },
    "Gaming / Skill Platforms": {
      "Dream11": ["Contest Entry", "Match Fantasy"],
      "MPL": ["Game Purchase", "Entry Fee"]
    }
  },

  "Health & Fitness": {
    "Pharmacies": {
      "Apollo Pharmacy": ["Paracetamol 10pcs", "Cough Syrup", "Multivitamins"],
      "1mg": ["Prescription Medicine", "Health Supplement"]
    },
    "Hospitals & Clinics": {
      "Fortis": ["Consultation Fee", "OPD Charge"],
      "Apollo Hospitals": ["OPD", "Lab Test"]
    },
    "Diagnostics": {
      "Dr Lal PathLabs": ["Blood Test", "COVID RT-PCR"],
      "SRL Diagnostics": ["Full Body Checkup"]
    },
    "Gyms & Wellness": {
      "Cult.Fit": ["Monthly Membership", "PT Session"],
      "Gold's Gym": ["Annual Membership"]
    }
  },

  "Education": {
    "Online Courses / Tutors": {
      "Byju's": ["Annual Subscription", "Crash Course"],
      "Unacademy": ["Course Pack", "Mock Test Series"]
    },
    "Books & Stationery": {
      "Sapna Book House": ["Textbook", "Notebook", "Pen"],
      "Crossword": ["Fiction Book", "Children's Book"]
    },
    "Institutions (fees)": {
      "Delhi University": ["Semester Fee"],
      "IIT Bombay": ["Exam Fee"]
    }
  },

  "Miscellaneous": {
    "Gifts & Flowers": {
      "Ferns N Petals": ["Flower Bouquet", "Cake Delivery"],
      "Archies": ["Greeting Card", "Gift Wrap"]
    },
    "Charities & Donations": {
      "GiveIndia": ["Donation"],
      "Akshaya Patra": ["Donation"]
    },
    "Pets & Petcare": {
      "Heads Up For Tails": ["Dog Food", "Pet Toy"],
      "Pet Stores Local": ["Pet Shampoo", "Pet Accessories"]
    },
    "Local Services / Small Shops": {
      "Local Tailor": ["Stitching Charge", "Alteration"],
      "Neighborhood Kirana": ["Small Purchase", "Milk"]
    }
  },

  "Home & Lifestyle": {
    "Furniture": {
      "Pepperfry": ["Sofa", "Dining Table", "Office Chair"],
      "Urban Ladder": ["Bed", "Wardrobe"]
    },
    "Home Appliances": {
      "LG India": ["Washing Machine", "Refrigerator"],
      "Samsung Stores": ["TV", "Microwave"]
    },
    "Home Décor & Furnishings": {
      "FabIndia Home": ["Cushion Cover", "Table Runner"],
      "Chumbak": ["Decor Item", "Planter"]
    }
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


def generate_dataset(n , force_cat = None):
    rows = []
    for _ in range(n):
        if force_cat:
            category = force_cat
        else:
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

df = generate_dataset(20000)
df.to_csv("expense_dataset.csv" , index=False)
print(df.head(10));


