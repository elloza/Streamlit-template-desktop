"""
Error page component for displaying friendly error messages.
Implements FR-016: Display friendly error page for invalid navigation.
"""
import streamlit as st
import traceback


def render(error: Exception = None, context: str = None):
    """
    Render a friendly error page.

    Args:
        error: The exception that occurred (optional)
        context: Additional context about the error (optional)
    """
    st.error("⚠️ An Error Occurred")

    st.markdown("""
    We're sorry, but something went wrong while loading this page.

    **What you can do:**
    - Try navigating to a different page using the sidebar
    - Check that all page modules are properly installed
    - Review the logs in `logs/app.log` for details
    """)

    if context:
        st.info(f"**Context**: {context}")

    if error:
        st.warning(f"**Error**: {str(error)}")

        with st.expander("Technical Details (for debugging)"):
            st.code(traceback.format_exc())

    # Provide navigation back to home
    st.markdown("---")
    st.markdown("🏠 **[Return to Home Page](#home)**")
