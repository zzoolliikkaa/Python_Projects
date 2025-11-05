from __future__ import annotations

import json
import logging
import re
from typing import Dict, List

import streamlit as st

# ---------- Configuration ----------
PHONEBOOK_JSON_FILENAME = "orig_texas_phonebook.json"
logger = logging.getLogger(__name__)
st.set_page_config(page_title="Phonebook", layout="wide", page_icon="📒")


# ---------- Utilities ----------
def init_state() -> None:
    """
    Initialize Streamlit session_state with a default phonebook.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    if "phonebook" not in st.session_state:
        phonebook = upload_json_file(PHONEBOOK_JSON_FILENAME)
        if phonebook:
            st.session_state.phonebook = phonebook
            logger.info("Loaded phonebook from JSON file.")
        else:
            logger.warning("Failed to load phonebook from JSON file.")
            logger.info("Using default phonebook.")
            st.session_state.phonebook = {
                "Alice Johnson": {
                    "phone_number": "+1 202 555 0173",
                    "email": "alice@example.com",
                    "address": "33828 Rhonda Hill Apt. 539",
                    "city": "New Troyhaven",
                    "state": "Texas",
                    "country": "USA",
                },
                "Bogdan Ionescu": {
                    "phone_number": "+40 21 555 3322",
                    "email": "bogdan@example.com",
                    "address": "123 Main St",
                    "city": "Bucharest",
                    "state": "Bucharest",
                    "country": "Romania",
                },
                "Csilla Kovács": {
                    "phone_number": "+36 30 555 1122",
                    "email": "csilla@example.com",
                    "address": "456 Elm St",
                    "city": "Budapest",
                    "state": "Budapest",
                    "country": "Hungary",
                },
            }
    if "mode" not in st.session_state:
        st.session_state.mode = "List"


def set_mode(new_mode: str) -> None:
    """
    Helper to switch the current view mode.

    Args:
        new_mode (str): The new mode to set for the view.

    Returns:
        None

    Raises:
        None
    """
    st.session_state.mode = new_mode


def as_table(data: Dict[str, Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Convert dict representation to a list of rows for display.

    Args:
        data (Dict[str, Dict[str, str]]): The phonebook data to convert.

    Returns:
        List[Dict[str, str]]: List of rows suitable for display in a table.

    Raises:
        None
    """
    return [
        {
            "Name": name,
            "Phone number": info.get("phone_number", ""),
            "Address": info.get("address", ""),
            "Email": info.get("email", ""),
            "City": info.get("city", ""),
            "State": info.get("state", ""),
            "Country": info.get("country", ""),
        }
        for name, info in sorted(data.items(), key=lambda kv: kv[0].lower())
    ]


def is_valid_email(value: str) -> bool:
    """
    Very light email validation (good enough for UI).

    Args:
        value (str): The email address to validate.

    Returns:
        bool: True if valid or empty, False otherwise.

    Raises:
        None
    """
    if not value:
        return True
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value) is not None


def is_valid_phone(value: str) -> bool:
    """
    Loose phone validation: digits, spaces, dashes, parentheses, plus.

    Args:
        value (str): The phone number to validate.

    Returns:
        bool: True if valid, False otherwise.

    Raises:
        None
    """
    if not value:
        return False
    return re.match(r"^[\d\s\-\+\(\)]+$", value) is not None


def upload_json_file(filename: str | None = None) -> dict:
    """
    Loads and validates a JSON file as a phonebook dict. Returns dict or None if invalid.

    Args:
        filename (str): Path to the JSON file.

    Returns:
        dict: Validated phonebook dict, or None if file is missing/invalid.
    """
    if not filename:
        return None
    try:
        # If filename is a file-like object (from st.file_uploader), use it directly
        if hasattr(filename, "read"):
            loaded = json.load(filename)
        else:
            with open(filename, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        if isinstance(loaded, dict) and all(
            isinstance(k, str) and isinstance(v, dict) for k, v in loaded.items()
        ):
            return loaded
    except Exception:
        pass
    return None


def Phonebook_main() -> None:
    """
    Main function to run the Streamlit Phonebook application.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    # ---------- Initialization ----------
    init_state()

    # ---------- Sidebar ----------
    with st.sidebar:
        st.markdown("### 📒 Phonebook")
        col = st.container()
        col.button(
            "📋  List", use_container_width=True, on_click=set_mode, args=("List",)
        )
        col.button(
            "🔎  Search", use_container_width=True, on_click=set_mode, args=("Search",)
        )
        col.button(
            "📝  Add", use_container_width=True, on_click=set_mode, args=("Add",)
        )
        col.button(
            "🗑️  Delete", use_container_width=True, on_click=set_mode, args=("Delete",)
        )

        st.divider()
        st.caption("Data")
        # Export current phonebook to JSON file
        if st.button("⬇️  Save phonebook to file", use_container_width=True):
            try:
                with open(PHONEBOOK_JSON_FILENAME, "w", encoding="utf-8") as f:
                    json.dump(
                        st.session_state.phonebook, f, ensure_ascii=False, indent=2
                    )
                st.success(f"Phonebook saved to {PHONEBOOK_JSON_FILENAME}")
            except Exception as e:
                st.error(f"Failed to save phonebook: {e}")

        uploaded = st.file_uploader("⬆️  Import JSON", type=["json"])
        if uploaded is not None:
            phonebook = upload_json_file(uploaded)
            if phonebook:
                st.session_state.phonebook = phonebook
                st.success("Imported phonebook.")
                st.toast("Import completed")
            else:
                st.error("Invalid or corrupted JSON file.")

    # ---------- Header ----------
    st.title("Phonebook")
    st.divider()

    # ---------- Views ----------
    mode = st.session_state.mode

    if mode == "List":
        logger.info("Listing all contacts.")
        st.subheader("All contacts")
        st.dataframe(
            as_table(st.session_state.phonebook),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Name": st.column_config.TextColumn(required=True),
                "Phone_number": st.column_config.TextColumn(
                    help="e.g. +1 202 555 0123"
                ),
                "Address": st.column_config.TextColumn(),
                "Email": st.column_config.TextColumn(help="name@example.com"),
                "City": st.column_config.TextColumn(),
                "State": st.column_config.TextColumn(),
                "Country": st.column_config.TextColumn(),
            },
        )
        st.caption(f"Total: {len(st.session_state.phonebook)} contact(s)")

    elif mode == "Search":
        logger.info("Searching contacts.")
        st.subheader("Search contacts")
        q = st.text_input("Type a name, phone, email, city, or country to filter")
        data = st.session_state.phonebook
        if q:
            q_lower = q.lower().strip()
            filtered = {
                name: info
                for name, info in data.items()
                if q_lower in name.lower()
                or q_lower in info.get("phone_number", "").lower()
                or q_lower in info.get("email", "").lower()
                or q_lower in info.get("city", "").lower()
                or q_lower in info.get("country", "").lower()
            }
        else:
            filtered = data

        st.caption(f"Showing {len(filtered)} of {len(data)} contacts")
        st.dataframe(
            as_table(filtered),
            use_container_width=True,
            hide_index=True,
        )

    elif mode == "Add":
        st.subheader("Add a new contact")
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Name *")
                phone = st.text_input("Phone *")
                email = st.text_input("Email")
            with c2:
                city = st.text_input("City")
                state = st.text_input("State/Region")
                country = st.text_input("Country")

            submitted = st.form_submit_button("Add")
            if submitted:
                logger.info("Adding a new contact.")
                # Validations
                if not name or not phone:
                    logger.warning("Name and Phone are required.")
                    st.error("Name and Phone are required.")
                elif not is_valid_phone(phone):
                    logger.warning("Invalid phone number entered.")
                    st.error("Please enter a valid phone number.")
                elif not is_valid_email(email):
                    logger.warning("Invalid email address entered.")
                    st.error("Please enter a valid email address.")
                elif name in st.session_state.phonebook:
                    logger.warning("A contact with this name already exists.")
                    st.warning("A contact with this name already exists.")
                else:
                    st.session_state.phonebook[name] = {
                        "phone_number": phone,
                        "email": email,
                        "address": "",
                        "city": city,
                        "state": state,
                        "country": country,
                    }
                    st.success(f"Added: {name}")
                    st.toast(f"Added {name}")

    elif mode == "Delete":
        st.subheader("Delete contacts")
        names = list(sorted(st.session_state.phonebook.keys(), key=str.lower))
        to_delete = st.multiselect("Select contact(s) to delete", names)
        if st.button("Delete selected", type="primary", disabled=not to_delete):
            for n in to_delete:
                st.session_state.phonebook.pop(n, None)
            st.success(f"Deleted {len(to_delete)} contact(s).")
            st.toast("Deletion completed")
            logger.info("Deleted contacts")

    # ---------- Footer / Help ----------
    with st.expander("ℹ️  Help"):
        st.markdown(
            f"""
    - Use the sidebar to switch between **List**, **Search**, **Add**, and **Delete**.
    - Use **Save phonebook to file** to persist data to `{PHONEBOOK_JSON_FILENAME}`.
    - Use **Import JSON** to load a phonebook from a JSON file.
    - For production, plug in a real database or file storage.
            """
        )


if __name__ == "__main__":
    Phonebook_main()
