# -*- coding:utf-8 -*-
"""
 作者: QL
 日期: 2023年01月18日
"""
import time
import pandas as pd
import streamlit as st
import pdfplumber
from PyPDF2 import PdfReader

a = st.radio("Type of Result Display:", ("Stock Code Oriented", "Third Level Issue Oriented"))
with st.spinner('Wait for it...'):
    if a == "Stock Code Oriented":
        time.sleep(2)
        st.write(a)
st.success("Done!")
# f = st.file_uploader("load pdf", help="load pdf here", label_visibility="collapsed")
# if f:
#     pdf = PdfReader(f)
#     outline_dict = pdf.outline
#     st.write(outline_dict)
# if pdf_path:
#     with open(pdf_path, "rb") as f:
#         pdf = PdfReader(f)
#         outline_dict = pdf.outline
#         st.write(outline_dict)