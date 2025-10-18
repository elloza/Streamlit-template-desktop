"""
Feature 1 example page - Demonstrates basic Streamlit widgets.
"""
import streamlit as st


def render():
    """Render Feature 1 page with widget examples."""
    st.title("⚙️ Feature 1: Widget Examples")

    st.markdown("""
    This page demonstrates various Streamlit widgets you can use in your application.
    """)

    # Input widgets
    st.subheader("Input Widgets")

    col1, col2 = st.columns(2)

    with col1:
        text = st.text_input("Text Input", "")
        number = st.number_input("Number Input", min_value=0, max_value=100, value=50)
        date = st.date_input("Date Picker")

    with col2:
        slider = st.slider("Slider", 0, 100, 25)
        checkbox = st.checkbox("Checkbox")
        radio = st.radio("Radio Buttons", ["Option A", "Option B", "Option C"])

    # Display results
    st.markdown("---")
    st.subheader("Results")

    if text:
        st.write(f"**Text**: {text}")
    st.write(f"**Number**: {number}")
    st.write(f"**Date**: {date}")
    st.write(f"**Slider**: {slider}")
    st.write(f"**Checkbox**: {'Checked' if checkbox else 'Unchecked'}")
    st.write(f"**Radio**: {radio}")

    # File uploader example
    st.markdown("---")
    st.subheader("File Upload")

    uploaded_file = st.file_uploader("Choose a file", type=["txt", "csv", "json"])
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        st.info(f"File size: {uploaded_file.size} bytes")

    # Button example
    st.markdown("---")
    if st.button("Click Me!"):
        st.balloons()
        st.success("Button clicked! 🎉")

    st.markdown("---")
    st.caption("Modify this page in `src/ui/pages/feature1.py`")
