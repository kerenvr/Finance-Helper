import csv
import mysql.connector
import os
from dotenv import load_dotenv
import numpy as np
from csv_prediction import category_prediction

load_dotenv()

users = [[] for _ in range(5)]


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

transactions = []

with open('./purchase tracker/may_june.csv', newline='\n') as csvfile:
    # Read the csv file
    spamreader = csv.reader(csvfile)
    for row in spamreader:  # Each row contains transaction information for a purchase
        temp = []  # Temporary list to store the row
        for item in row:
            temp.append(item.replace(' ', ''))
        transactions.append(temp)

for transaction in transactions:
    try:
        credit_card = transaction[0]
        buyer = int(transaction[1])  # Person responsible for the transaction
        date = transaction[2]
        amount = float(transaction[3])  # Price of the transaction
        description = transaction[4]  # Store / Company
        paid = transaction[5]  # Track if buyer has paid me back
        notes = transaction[6]

        # If this row is not empty
        if paid != '':
            # Get each buyer individually (separated by commas)
            persons = paid.split(',')
            for person in persons:
                name, answer_and_amount_owed = person.split(':')
                answer, amount_owed = answer_and_amount_owed.split('|')

                # Clean the data
                answer = answer.strip('[')  # Yes or No
                amount_owed = amount_owed.strip(
                    ']').strip("$")  # Amount owed or payed

                # print(name, answer)

                # Sometimes the name will not be an int (I reference frequent users as integers,
                # but the other people that don't normally use my cards are not part of this)
                try:
                    if answer == "Yes":
                        users[int(name)].append(-float(amount_owed))
                    if answer == 'No':
                        users[0].append(-float(amount_owed))
                        users[int(name)].append(float(amount_owed))

                except:
                    continue

    except:
        continue

    # Check who buyer is

    # Check if buyer is me
    if buyer == 0:
        users[0].append(amount)
    elif buyer == 1:
        users[1].append(amount)
    elif buyer == 2:
        users[2].append(amount)
    elif buyer == 3:
        users[3].append(amount)
    elif buyer == 4:
        users[4].append(amount)

# Predict categories for purchases
category_prediction('./purchase tracker/may_june.csv', 4)
print(description, category_prediction)

for i in range(5):
    person_name = os.environ.get(f'PERSON_NAME{i}')
    total_owed = round(sum(users[i]), 2)
    if total_owed > 0:
        print(f"{person_name}: ${total_owed}")
