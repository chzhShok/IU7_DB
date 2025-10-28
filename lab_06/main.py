from streaming_service_db import StreamingServiceDB


def menu():
    print("\n----- MENU -----")
    print("1. Execute scalar query")
    print("2. Execute multi-join query")
    print("3. Execute query with CTE and window functions")
    print("4. Execute metadata query")
    print("5. Call scalar function")
    print("6. Call multi-statement or table-valued function")
    print("7. Call stored procedure")
    print("8. Call system function or procedure")
    print("9. Create table in database")
    print("10. Insert data into created table using INSERT or COPY")
    print("11. Drop database")
    print("0. Exit")


def main():
    db = StreamingServiceDB()

    while True:
        menu()
        choice = input("\n\nSelect menu item: ").strip()
        if choice == "1":
            res = db.avg_movies_release_year()
            print(f"Average movies release year: {res:0.2f}")

        elif choice == "2":
            res = db.users_statistic()
            print(f"Users statistic\n")
            print(res)

        elif choice == "3":
            res = db.movies_rating()
            print(f"Movies rating\n")
            print(res)

        elif choice == "4":
            res = db.table_columns_information()
            print(f"Table columns information\n")
            print(res)

        elif choice == "5":
            res = db.director_avg_rating()
            print(f"Director average rating\n")
            print(res)

        elif choice == "6":
            subscription_type = input("Subscription type: ").strip()
            if subscription_type not in ['basic', 'standard', 'premium']:
                print("Subscription type must be 'basic', 'standard' or 'premium'")
            else:
                res = db.users_by_subscription(subscription_type)
                print(f"Users by subscription {subscription_type}\n")
                print(res)

        elif choice == "7":
            user_id = int(input("User ID: "))
            new_subscription = input("New subscription: ")
            res = db.update_user_subscription(user_id, new_subscription)
            print("Updated user subscription")
            print(res)

        elif choice == "8":
            res = db.database_size()
            print(f"Database size\n")
            print(res)

        elif choice == "9":
            db.create_review_table()

        elif choice == "10":
            res = db.insert_user_review()
            print(res)

        elif choice == "11":
            db.drop_database()

        elif choice == "0":
            print("Exit program")
            break

        else:
            print("Wring choice")


if __name__ == "__main__":
    main()
