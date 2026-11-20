"""
AgriYield Pro entry point (Team 11).

Routes between two views of the same model and data:
  /          classic_page.py  (the submitted interface, unchanged)
  /updated   updated_page.py  (refreshed field-green interface)

Navigation is hidden, so the home page looks exactly as before; the updated view is
reached through a small link at the bottom of the home page or directly by URL.
"""

from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent

pages = [
    st.Page(APP_DIR / "classic_page.py", title="AgriYield Pro", url_path="classic", default=True),
    st.Page(APP_DIR / "updated_page.py", title="AgriYield", url_path="updated"),
]
st.navigation(pages, position="hidden").run()
