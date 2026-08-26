import streamlit as st


def render_download_button(df, filename, label="Download CSV"):
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=filename,
        mime='text/csv'
    )
