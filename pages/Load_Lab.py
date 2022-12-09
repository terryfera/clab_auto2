import streamlit as st
import utils
import json
import config
from git import Repo
import os
from pathlib import Path
from tinydb import TinyDB, Query

def load_page():
    labs_list = utils.get_db_labs()
    with st.form("load lab"):
        st.write("Lab loading form")
        option = st.selectbox(
            'Select a lab:', labs_list
        )
        submitted = st.form_submit_button("Submit")
        if submitted:
            with st.spinner(text="Checking if lab is already running"):
                lab_check = utils.clab_function("inspect", option)
            if lab_check is None:
                st.write("Lab does not exist, you shouldn't see this")
            elif type(lab_check) is str:
                st.warning("Lab doesn't exist, check that topology file exists:", icon="⚠️")
                st.text(lab_check)
            elif lab_check.returncode == 0 and lab_check.stdout == '':
                with st.spinner(text="Lab loading..."):
                    lab = utils.clab_function("deploy", option)
                st.success("Complete")
                if lab.returncode == 0:
                    st.success('Lab loaded successfully!', icon="✅")
                    with st.expander("Lab load details"):
                        st.code(lab.stdout)
                    st.subheader("Logs")
                    with st.expander("Lab load logs"):
                        st.text(lab.stderr)
                elif lab.returncode == 1:
                    st.error("There was a problem loading the lab")

                    with st.expander("Lab load logs"):
                        st.text(lab.stderr)
            elif lab_check.returncode == 0 and lab_check.stdout is not None:
                st.warning('Lab is already running', icon="⚠️")
                with st.expander("Running lab details"):
                    st.code(utils.clab_function("inspect", option).stdout)
            elif lab_check.returncode == 1:
                st.error('Error checking if lab is running', icon="🚨")



if __name__ == "__main__":
    load_page()