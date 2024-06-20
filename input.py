from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Example data (replace with your actual dataset)
db_user = os.getenv('DB_USER')
db_host = os.getenv('DB_HOST')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT') or '3306'
db_name = os.getenv('DB_DATABASE')


def update_database(name_to_predict, correct_category):
    try:
        # Establish a new connection to update the database
        cnx = mysql.connector.connect(user=db_user,
                                      host=db_host,
                                      password=db_password,
                                      port=db_port,
                                      database=db_name)

        # Create a cursor object to interact with the database
        mycursor = cnx.cursor()

        # Execute SQL update query
        update_query = "INSERT INTO Categories (PurchaseName, Category) VALUES (%s, %s)"
        mycursor.execute(update_query, (name_to_predict, correct_category))

        # Commit the changes
        cnx.commit()

        # Close the cursor and database connection
        mycursor.close()
        cnx.close()

        print(
            f"Database updated successfully! {name_to_predict} updated to {correct_category}.")
    except mysql.connector.Error as err:
        print(f"Error updating database: {err}")

# Main process to predict and update database based on user input


def main():
    while True:

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

        # Train the model (replace with your actual training process)
        model.fit(X_train, y_train)

        to_predict = input(
            "Input a name to predict (or type 'exit' to quit): ")

        if to_predict.lower() == 'exit':
            print("Exiting...")
            break

        # Predictions
        predicted = model.predict([to_predict])[0]

        # Output the prediction
        print(f"Predicted category for {to_predict}: {predicted}")

        correct = input("Was this prediction correct? (y/n): ")

        if correct.lower() == "y":
            print("Great! Have a nice day!")
        else:
            print("I'm sorry to hear that. Let me update the database for you.")
            print(
                "Categories: Food, Transportation, Grocery, Retail, Subscription, Recreation, Business and Technology Services")
            correct_category = input(
                f"What was the correct category for {to_predict}? ")

            # Call function to update database
            update_database(to_predict.upper(), correct_category)


if __name__ == "__main__":
    main()
