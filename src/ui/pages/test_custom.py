"""
Test custom page to verify extensibility feature (T044).
This page demonstrates that users can add new pages dynamically.
"""
import streamlit as st


def render():
    """Render test custom page content"""
    st.title("🧪 Test Custom Page")

    st.success("✅ Success! This custom page was added dynamically.")

    st.write("""
    This page demonstrates the template's extensibility features:
    - Created a new page module (`src/ui/pages/test_custom.py`)
    - Added menu item to `config/app.yaml`
    - Page appears in sidebar automatically
    - No code changes needed in navigation system
    """)

    # Example widgets
    st.subheader("Example Widgets")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Sample Input", value="Hello World!")
        st.slider("Sample Slider", 0, 100, 50)

    with col2:
        st.selectbox("Sample Dropdown", ["Option 1", "Option 2", "Option 3"])
        st.checkbox("Sample Checkbox", value=True)

    st.info("💡 To add your own pages, see `docs/extending.md`")
