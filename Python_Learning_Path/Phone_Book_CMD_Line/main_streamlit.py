import json
import os

import streamlit as st


def clear_screen():
    """Clears the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def load_phonebook(file_path):
    """Load phonebook data where keys are phone numbers."""
    if not os.path.exists(file_path):
        print("File not found. Starting with an empty phonebook.")
        input()
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure all keys are strings and values are dictionaries
    phonebook_by_number = {}
    for phone_number, info in data.items():
        if isinstance(info, dict):
            phonebook_by_number[str(phone_number)] = {
                "name": info.get("name", ""),
                "email": info.get("email", ""),
                "address": info.get("address", ""),
                "city": info.get("city", ""),
                "state": info.get("state", ""),
                "country": info.get("country", ""),
            }
    return phonebook_by_number


def save_phonebook(file_path, phonebook_by_number):
    """Atomically save the phonebook (keyed by phone number) to JSON."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(phonebook_by_number, f, indent=4)


def add_contact():
    """Add a contact if phone number not present; persist to JSON."""
    phone_number = input("Enter phone number: ")
    print(phone_number)
    print(phone_number in phonebook_by_number)
    if phone_number in phonebook_by_number:
        print("Contact with this phone number already exists.")
        return

    name = input("Enter name: ")
    email = input("Enter email: ")
    address = input("Enter address: ")
    city = input("Enter city: ")
    if city == "":
        city = "Austin"
    state = input("Enter state: ")
    if state == "":
        state = "TX"
    country = input("Enter country: ")
    if country == "":
        country = "USA"

    phonebook_by_number[phone_number] = {
        "name": name,
        "email": email,
        "address": address,
        "city": city,
        "state": state,
        "country": country,
    }
    search_by_number(phone_number)
    save_phonebook(json_file, phonebook_by_number)
    print("Contact added successfully.")


def search_by_number(number=None):
    """Search and print a contact by phone number."""
    if number is None:
        phone_number = input("Enter phone number to search: ")
    else:
        phone_number = number

    contact = phonebook_by_number.get(phone_number)
    if contact:
        print(
            f"\tNumber: {phone_number}, \n\tName: {contact['name']}, \n\tEmail: {contact['email']}, \n\tAddress: {contact['address']}, \n\tCity: {contact['city']}, \n\tState: {contact['state']}, \n\tCountry: {contact['country']}"
        )
    else:
        print("Contact not found.")


def list_all_contacts():
    """List all contacts."""
    if phonebook_by_number:
        print("Phonebook contacts:")
        for number, info in phonebook_by_number.items():
            print(
                f"\tNumber: {number}, \n\tName: {info['name']}, \n\tEmail: {info['email']}, \n\tAddress: {info['address']}, \n\tCity: {info['city']}, \n\tState: {info['state']}, \n\tCountry: {info['country']}"
            )
            print("-" * 80)
    else:
        print("No contacts found.")


# Load JSON file into a Python dictionary
json_file = "texas_phonebook.json"
phonebook_by_number = load_phonebook(json_file)


# # Simple command-line interface to interact with the phonebook
# while True:
#     clear_screen()
#     print("1 - Add new contact")
#     print("2 - Search by phone number")
#     print("3 - List all contacts")
#     print("4 - Exit")
#     choice = input("Choose an option (1-4): ")
#     if choice == "1":
#         add_contact()
#         input()
#     elif choice == "2":
#         search_by_number()
#         input()
#     elif choice == "3":
#         list_all_contacts()
#         input()
#     elif choice == "4":
#         break


phonebook = phonebook_by_number  # For Streamlit app
st.title("📞 Texas Phonebook")

menu = st.sidebar.selectbox("Choose an action", ["List all", "Search", "Add contact"])

if menu == "List all":
    st.subheader("All contacts")
    for number, info in phonebook.items():
        st.write(f"**{info['name']}** — {number}")
        st.write(f"{info['email']}, {info['city']}, {info['state']}, {info['country']}")
        st.divider()

elif menu == "Search":
    number = st.text_input("Enter phone number:")
    if st.button("Search"):
        contact = phonebook.get(number)
        if contact:
            st.success(f"Found: {contact['name']} ({number})")
            st.json(contact)
        else:
            st.error("Contact not found.")

elif menu == "Add contact":
    number = st.text_input("Phone number:")
    name = st.text_input("Name:")
    email = st.text_input("Email:")
    city = st.text_input("City:", "Austin")
    state = st.text_input("State:", "TX")
    country = st.text_input("Country:", "USA")

    if st.button("Save"):
        phonebook[number] = {
            "name": name,
            "email": email,
            "address": "",
            "city": city,
            "state": state,
            "country": country,
        }
        with open("texas_phonebook.json", "w", encoding="utf-8") as f:
            json.dump(phonebook, f, indent=4)
        st.success("✅ Contact added successfully!")
