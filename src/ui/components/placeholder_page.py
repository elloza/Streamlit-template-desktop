"""
Placeholder page component for unimplemented pages.
Implements FR-019: Show helpful instructions when page is missing.
"""
import streamlit as st


def render(module_path: str):
    """
    Render a placeholder page with implementation instructions.

    Args:
        module_path: The module path that was not found
    """
    st.warning("📝 Page Not Implemented")

    st.markdown(f"""
    The page module `{module_path}` has been added to the menu but hasn't been implemented yet.

    ### How to Implement This Page

    **Step 1: Create the page module**

    Create a new file at the module path with a `render()` function:

    ```python
    # {module_path.replace('.', '/')}.py
    import streamlit as st

    def render():
        '''Your page content here'''
        st.title("My New Page")
        st.write("Welcome to my custom page!")

        # Add your Streamlit components here
        name = st.text_input("Enter your name")
        if name:
            st.success(f"Hello, {{name}}!")
    ```

    **Step 2: Restart the application**

    After creating the file, restart the application to see your new page.

    ### Resources

    - 📚 [Streamlit Documentation](https://docs.streamlit.io)
    - 📖 [Template Extension Guide](docs/extending.md)
    - 💡 [Example Pages](src/ui/pages/)

    ### Quick Tips

    - Every page must have a `render()` function
    - Use Streamlit components (`st.*`) to build your UI
    - Keep page logic simple and focused
    - Handle errors gracefully with try/except blocks
    """)

    # Show example of working pages
    st.markdown("---")
    st.info("💡 **Tip**: Check out `src/ui/pages/home.py` for a working example!")
