import streamlit as st
import utils


def load_page():
    it_enabled = "False"
    git_url = ''
    if st.checkbox('Use Git Repo?'):
        git_enabled = "True"
        git_url = st.text_input('Git URL')

    host_dict = {
        "172.20.20.2": "show ip route",
        "172.20.20.3": "show ip route",
    }
    with st.form("ssh connection"):
        st.write("Lab Devices")
        option = st.selectbox(
            'Select a Device:', list(host_dict.keys())
        )


if __name__ == "__main__":
    load_page()
