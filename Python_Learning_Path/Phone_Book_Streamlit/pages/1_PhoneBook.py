import streamlit as st


def list_all_contacts():
    """List all contacts."""
    st.write("Listing all contacts...")


st.title("Simple Phonebook Application")
st.button("List Contacts", on_click=list_all_contacts)
