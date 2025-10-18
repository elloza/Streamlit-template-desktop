"""
Feature 2 example page - Demonstrates layout and data display.
"""
import streamlit as st
import pandas as pd


def render():
    """Render Feature 2 page with layout examples."""
    st.title("📊 Feature 2: Layouts & Data Display")

    st.markdown("""
    This page shows different layout options and data visualization components.
    """)

    # Columns layout
    st.subheader("Column Layout")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Metric 1", value="123", delta="5")
    with col2:
        st.metric(label="Metric 2", value="456", delta="-3")
    with col3:
        st.metric(label="Metric 3", value="789", delta="12")

    # Expander
    st.markdown("---")
    with st.expander("Click to expand"):
        st.write("This content is hidden inside an expander!")
        st.write("You can put any Streamlit components here.")

    # Tabs
    st.markdown("---")
    st.subheader("Tabs")

    tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

    with tab1:
        st.write("Content for Tab 1")
        st.info("This is an info box")

    with tab2:
        st.write("Content for Tab 2")
        st.warning("This is a warning box")

    with tab3:
        st.write("Content for Tab 3")
        st.success("This is a success box")

    # Data display
    st.markdown("---")
    st.subheader("Data Table")

    # Create sample data
    df = pd.DataFrame({
        'Column A': [1, 2, 3, 4, 5],
        'Column B': [10, 20, 30, 40, 50],
        'Column C': ['A', 'B', 'C', 'D', 'E']
    })

    st.dataframe(df, use_container_width=True)

    # Chart example
    st.subheader("Simple Chart")
    st.line_chart(df[['Column A', 'Column B']])

    st.markdown("---")
    st.caption("Modify this page in `src/ui/pages/feature2.py`")
