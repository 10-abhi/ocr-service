import random
import pandas as pd

#cat . subcat with merchants ex
categories = {
    "Food & Drinks": {
        "Coffee Shops": ["Café Coffee Day", "Starbucks", "Chai Point", "Barista"],
        "Restaurants": ["Dominos Pizza", "Haldiram's", "Biryani By Kilo", "Barbeque Nation", "McDonald's"],
        "Groceries": ["Big Bazaar", "DMart", "Reliance Fresh", "BigBasket", "Nature's Basket"]
    },
    "Transport": {
        "Taxi/Ride-hailing": ["Ola", "Uber", "Rapido"],
        "Fuel": ["IndianOil", "BPCL", "HPCL", "Shell"],
        "Public Transit": ["IRCTC", "Delhi Metro", "BMTC", "BEST"]
    },
    "Entertainment": {
        "Streaming": ["Hotstar", "SonyLIV", "JioCinema", "Netflix", "Spotify"],
        "Cinema": ["PVR", "INOX", "Cinepolis"],
        "Gaming": ["Dream11", "MPL", "Paytm First Games", "Steam"]
    },
    "Shopping": {
        "Online": ["Flipkart", "Amazon India", "Myntra", "Ajio"],
        "Clothing": ["FabIndia", "Pantaloons", "Westside", "Zara"],
        "Electronics": ["Croma", "Reliance Digital", "Vijay Sales", "Best Buy"]
    },
    "Bills & Utilities": {
        "Electricity": ["BESCOM", "TNEB", "MSEB", "BSES Rajdhani"],
        "Mobile/Internet": ["Jio", "Airtel", "VI", "BSNL"],
        "Water": ["BWSSB", "Delhi Jal Board"]
    },
    "Travel": {
        "Flights": ["IndiGo", "Vistara", "Air India", "SpiceJet"],
        "Hotels": ["OYO", "Taj Hotels", "ITC Hotels", "Treebo"],
        "Booking": ["MakeMyTrip", "Yatra", "Goibibo", "Expedia"]
    },
    "Health & Fitness": {
        "Pharmacy": ["Apollo Pharmacy", "NetMeds", "1mg", "MedPlus"],
        "Gym": ["Cult.Fit", "Gold's Gym", "Talwalkars"],
        "Insurance": ["LIC", "ICICI Lombard", "HDFC Ergo"]
    },
    "Education": {
        "Online Courses": ["Unacademy", "Byju's", "Vedantu", "Udemy"],
        "Books": ["Sapna Book House", "Crossword", "Amazon Kindle"],
        "University Fees": ["Delhi University", "IIT Bombay", "Anna University"]
    },
    "Finance": {
        "Banking Fees": ["SBI", "HDFC", "ICICI", "Axis Bank"],
        "UPI/Wallets": ["Paytm", "PhonePe", "Google Pay", "Freecharge"],
        "Investments": ["Zerodha", "Groww", "Paytm Money"]
    },
    "Miscellaneous": {
        "Charity": ["Akshaya Patra", "CRY", "GiveIndia", "Red Cross"],
        "Gifts": ["Ferns N Petals", "Archies", "IGP"],
        "Pets": ["Heads Up For Tails", "PetWorld", "Petco"]
    }
}

def generate_dataset(n):
    rows = []
    for _ in range(n):
        category = random.choice(list(categories.keys()))
        subcategory = random.choice(list(categories[category].keys()))
        merchant = random.choice(categories[category][subcategory])

        #some description variation
        templates = [
            f"{merchant} Purchase",
            f"{merchant} Bill Payment",
            f"Payment at {merchant}",
            f"{merchant} Subscription",
            f"Transaction at {merchant}"
        ]
        description = random.choice(templates)

        rows.append([description , category , subcategory])
    
    df = pd.DataFrame(rows , columns=["Description" , "Category" , "Subcategory"])
    return df

df = generate_dataset(3000)
df.to_csv("expense_dataset.csv" , index=False)
print(df.head(10));


