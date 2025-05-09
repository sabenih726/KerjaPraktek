# app.py

import streamlit as st
from pdf_convert import process_pdfs

# -------------------- LOGIN & SESSION --------------------

def login():
    """Simple login with hardcoded credentials."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔐 Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Daftar user dan password
        valid_users = {
            "sinta": "sinta123",
            "ainun": "ainun123",
            "fatih": "fatih123"
        }

        if username in valid_users and password == valid_users[username]:
            st.session_state.authenticated = True
            st.success("Login berhasil!")
            st.experimental_rerun()
        else:
            st.error("Username atau password salah.")

    return False


def logout():
    """Reset authentication session state."""
    st.session_state.authenticated = False
    st.success("Logout berhasil.")
    st.experimental_rerun()


def get_greeting():
    """Return greeting based on time."""
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 12:
        return "Selamat pagi"
    elif hour < 18:
        return "Selamat siang"
    else:
        return "Selamat malam"

# -------------------- MAIN APP --------------------

def main():
    if not login():
        return

    st.set_page_config(page_title="Ekstraksi PDF Imigrasi", layout="wide")

    st.title("📄 Aplikasi Ekstraksi Dokumen Imigrasi")
    st.markdown(f"👋 {get_greeting()}, selamat datang!")

    st.sidebar.title("Navigasi")
    st.sidebar.write("Pilih pengaturan:")
    if st.sidebar.button("Logout"):
        logout()

    # Input
    uploaded_files = st.file_uploader("Unggah satu atau beberapa file PDF", type="pdf", accept_multiple_files=True)
    doc_type = st.selectbox("Pilih jenis dokumen", ["SKTT", "EVLN", "ITAS", "ITK", "Notifikasi"])
    use_name = st.checkbox("Gunakan nama dalam nama file")
    use_passport = st.checkbox("Gunakan nomor paspor dalam nama file")

    if st.button("🔍 Proses"):
        if not uploaded_files:
            st.warning("Harap unggah minimal satu file PDF.")
        else:
            with st.spinner("Memproses dokumen..."):
                df, excel_path, renamed_files, zip_path, temp_dir = process_pdfs(
                    uploaded_files, doc_type, use_name, use_passport
                )
                st.success("Ekstraksi selesai!")

                st.download_button("📥 Unduh Hasil Excel", open(excel_path, "rb").read(), file_name="Hasil_Ekstraksi.xlsx")
                st.download_button("📦 Unduh File ZIP", open(zip_path, "rb").read(), file_name="Hasil_Rename.zip")

                st.subheader("📊 Data yang Diekstrak")
                st.dataframe(df)

                st.subheader("📝 Daftar File Rename")
                for original, info in renamed_files.items():
                    st.write(f"{original} ➜ {info['new_name']}")

if __name__ == "__main__":
    main()
