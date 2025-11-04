
# streamlit run phonebook_streamlit.py
# Phonebook demo using Streamlit
# Comments are in English as requested.

import streamlit as st
from typing import Dict, List

st.set_page_config(page_title="Phonebook", layout="wide", page_icon="📒")

# ---------- Utilities ----------
def init_state() -> None:
    """Initialize Streamlit session_state with a default phonebook."""
    if "phonebook" not in st.session_state:
        st.session_state.phonebook: Dict[str, Dict[str, str]] = {
            "Alice Johnson": {"phone": "+1 202 555 0173", "email": "alice@example.com"},
            "Bogdan Ionescu": {"phone": "+40 21 555 3322", "email": "bogdan@example.com"},
            "Csilla Kovács": {"phone": "+36 30 555 1122", "email": "csilla@example.com"},
        }
    if "mode" not in st.session_state:
        st.session_state.mode = "List"

def set_mode(new_mode: str) -> None:
    """Helper to switch the current view mode."""
    st.session_state.mode = new_mode

def as_table(data: Dict[str, Dict[str, str]]) -> List[Dict[str, str]]:
    """Convert dict representation to a list of rows for display."""
    return [
        {"Name": name, "Phone": info.get("phone", ""), "Email": info.get("email", "")}
        for name, info in sorted(data.items(), key=lambda kv: kv[0].lower())
    ]

init_state()

# ---------- Sidebar (matches buttons from the screenshot) ----------
with st.sidebar:
    st.markdown("### 📒 Phonebook")
    col1 = st.container()
    col1.button("➕  List", use_container_width=True, on_click=set_mode, args=("List",))
    col1.button("🔎  Search", use_container_width=True, on_click=set_mode, args=("Search",))
    col1.button("📝  Add", use_container_width=True, on_click=set_mode, args=("Add",))
    col1.button("🗑️  Delete", use_container_width=True, on_click=set_mode, args=("Delete",))

    with st.expander("⚙️  Settings / Menu"):
        st.write("Menu item")
        st.write("Menu item")
        st.write("Menu item")
        st.write("Menu item")

# ---------- Header ----------
st.title("Phonebook")

st.divider()

# ---------- Views ----------
mode = st.session_state.mode

if mode == "List":
    st.subheader("All contacts")
    st.dataframe(as_table(st.session_state.phonebook), use_container_width=True, hide_index=True)

elif mode == "Search":
    st.subheader("Search contacts")
    q = st.text_input("Type a name, phone, or email to filter")
    data = st.session_state.phonebook
    if q:
        q_lower = q.lower().strip()
        filtered = {
            name: info
            for name, info in data.items()
            if q_lower in name.lower()
            or q_lower in info.get("phone", "").lower()
            or q_lower in info.get("email", "").lower()
        }
    else:
        filtered = data

    st.caption(f"Showing {len(filtered)} of {len(data)} contacts")
    st.dataframe(as_table(filtered), use_container_width=True, hide_index=True)

elif mode == "Add":
    st.subheader("Add a new contact")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name *")
        phone = st.text_input("Phone *")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Add")
        if submitted:
            # Simple validations
            if not name or not phone:
                st.error("Name and Phone are required.")
            elif name in st.session_state.phonebook:
                st.warning("A contact with this name already exists.")
            else:
                st.session_state.phonebook[name] = {"phone": phone, "email": email}
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

# ---------- Footer / Help ----------
with st.expander("ℹ️  Help"):
    st.markdown(
        """
- Use the sidebar to switch between **List**, **Search**, **Add**, and **Delete**.
- Data is stored in `st.session_state` (in-memory) for demo purposes.
- To persist data, replace the storage with a database or file I/O.
        """
    )
