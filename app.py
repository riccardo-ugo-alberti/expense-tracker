from __future__ import annotations

from hashlib import sha256
from io import BytesIO

import pandas as pd
import streamlit as st

from src.db.connection import get_session, init_db
from src.db.repository import FinanceRepository


SUPPORTED_FILE_TYPES = ["csv", "xls", "xlsx"]


def load_preview(uploaded_file) -> pd.DataFrame:
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if file_name.endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))

    return pd.read_excel(BytesIO(file_bytes))


def build_import_signature(account_id: int, uploaded_file, row_count: int) -> str:
    file_bytes = uploaded_file.getvalue()
    digest = sha256(file_bytes).hexdigest()
    suffix = uploaded_file.name.rsplit(".", 1)[-1].lower()
    return f"{account_id}:{uploaded_file.name}:{suffix}:{row_count}:{digest}"


def create_account_form() -> None:
    st.subheader("Create your first account")
    st.caption("Add at least one account before previewing manual bank exports.")

    with st.form("create_account_form", clear_on_submit=True):
        bank_name = st.text_input("Bank name", placeholder="Cortina Banca / Inbank")
        account_name = st.text_input("Account name", placeholder="Main checking")
        account_type = st.text_input("Account type", placeholder="Checking")
        currency = st.text_input("Currency", value="EUR", max_chars=3)
        submitted = st.form_submit_button("Create account")

    if not submitted:
        return

    if not bank_name.strip() or not account_name.strip():
        st.error("Bank name and account name are required.")
        return

    with get_session() as session:
        repository = FinanceRepository(session)
        repository.create_account(
            bank_name=bank_name.strip(),
            account_name=account_name.strip(),
            account_type=account_type.strip() or None,
            currency=currency.strip().upper() or "EUR",
        )

    st.success("Account created.")
    st.rerun()


def main() -> None:
    st.set_page_config(page_title="Expense Tracker", layout="centered")
    init_db()

    st.title("Expense Tracker")
    st.write(
        "A simple multi-account personal finance workspace for manual bank exports."
    )
    st.write(
        "This app will consolidate multiple bank accounts into one unified system. "
        "Bank accounts are treated as transaction sources, and previewed imports "
        "will feed a single database and dashboard over time."
    )

    with get_session() as session:
        repository = FinanceRepository(session)
        accounts = list(repository.list_accounts())

    if not accounts:
        create_account_form()
        st.info("No accounts found yet. Create an account to continue.")
        return

    st.subheader("Import preview")
    account_options = {
        f"{account.bank_name} - {account.account_name} ({account.currency})": account.id
        for account in accounts
    }
    selected_label = st.selectbox(
        "Select the account this file belongs to",
        options=list(account_options.keys()),
        index=None,
        placeholder="Choose an account",
    )
    selected_account_id = account_options[selected_label] if selected_label else None

    uploaded_file = st.file_uploader(
        "Upload a bank export",
        type=SUPPORTED_FILE_TYPES,
        help="CSV, XLS, and XLSX files are supported for preview.",
    )

    st.caption(
        "This preview is intentionally generic. Bank-specific schemas and transaction writes "
        "will be added later after sample files are reviewed."
    )

    if uploaded_file is None:
        return

    try:
        preview = load_preview(uploaded_file)
    except Exception as exc:
        st.error(f"Could not preview this file: {exc}")
        return

    if selected_account_id is None:
        st.error("Select an account before saving this import.")

    file_type = uploaded_file.name.rsplit(".", 1)[-1].lower()
    row_count = len(preview)
    import_signature = build_import_signature(selected_account_id or 0, uploaded_file, row_count)
    last_saved_signature = st.session_state.get("last_saved_import_signature")
    already_saved = last_saved_signature == import_signature

    st.write(f"Selected account ID: `{selected_account_id}`" if selected_account_id else "Selected account ID: `None`")
    st.write(f"Uploaded file: `{uploaded_file.name}`")
    st.success("File loaded successfully.")
    st.dataframe(preview.head(20), use_container_width=True)
    st.caption(f"Previewing {min(row_count, 20)} of {row_count} rows.")

    if already_saved:
        st.info("This import preview has already been saved in the current session.")

    if st.button("Save import", disabled=selected_account_id is None or already_saved):
        if selected_account_id is None:
            st.error("Select an account before saving this import.")
            return

        try:
            with get_session() as session:
                repository = FinanceRepository(session)
                repository.create_import_run(
                    account_id=selected_account_id,
                    file_name=uploaded_file.name,
                    file_type=file_type,
                    row_count=row_count,
                    status="previewed",
                )
        except Exception as exc:
            st.error(f"Could not save import metadata: {exc}")
            return

        st.session_state["last_saved_import_signature"] = import_signature
        st.success("Import metadata saved.")


if __name__ == "__main__":
    main()
