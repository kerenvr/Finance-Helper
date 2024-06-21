import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
import mysql.connector
import os
from dotenv import load_dotenv
import numpy as np

# TODO: make this a function that takes a csv file, and the columns are parameters because
# with different csv files, they are different

load_dotenv()

# Example data (replace with your actual dataset)
db_user = os.getenv('DB_USER')
db_host = os.getenv('DB_HOST')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT') or '3306'
db_name = os.getenv('DB_DATABASE')

cnx = mysql.connector.connect(user=db_user,
                              host=db_host,
                              password=db_password,
                              port=db_port,
                              database=db_name)
mycursor = cnx.cursor()
mycursor.execute("SELECT PurchaseName, Category FROM Categories")

# Fetch all rows
results = mycursor.fetchall()

# Process the fetched data
names = []
categories = []
for name, category in results:
    names.append(name)
    categories.append(category)

# Close the cursor and database connection
mycursor.close()
cnx.close()

# Split data into training and testing sets (for demonstration, assuming you have actual data)
X_train, X_test, y_train, y_test = train_test_split(
    names, categories, test_size=0.2, random_state=42)

# Create a pipeline: TF-IDF vectorizer + Naive Bayes classifier
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

# Train the model
model.fit(X_train, y_train)

# Will store all transactions from the csv file
transactions = []


def category_prediction(csv_file, column_index):
    with open(csv_file, newline='\n') as csvfile:
        # Read the csv file
        spamreader = csv.reader(csvfile)
        for row in spamreader:  # Each row contains transaction information for a purchase
            temp = []  # Temporary list to store the row
            for item in row:
                temp.append(item)
            transactions.append(temp)

    for transaction in transactions:
        purchase_name = transaction[column_index]  # Name of purchase
        prediction = model.predict_proba([purchase_name])

        threshold = 0.2
        if np.max(prediction) >= threshold:
            predicted_category = model.predict([purchase_name])[0]
        else:
            predicted_category = "Unknown"

        print(f"Predicted category for {purchase_name}: {predicted_category}")
