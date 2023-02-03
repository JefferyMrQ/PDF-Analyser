# Import from standard library
import re
import time
import pandas as pd
from io import StringIO, BytesIO

# Import from 3rd party libraries
import streamlit as st
import pdfplumber
import jieba

# from pyxlsb import open_workbook as open_xlsb


def to_excel(df):
    """
    transfer pd.DataFrame to 'file-like' excel file
    :param df: dataframe to be transferred
    :return: excel file in the form of BytesIO value
    """
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=True, sheet_name='Sheet1')
    # workbook = writer.book
    # worksheet = writer.sheets['Sheet1']
    # format1 = workbook.add_format({'num_format': '0.00'})
    # worksheet.set_column('A:A', None, format1)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def assurance_keyword(pdf):
    """
    obtain the keyword matching result of a pdf file within a default page range
    :param pdf: opened pdf file data
    :return:
    """
    pattern_assurance = re.compile("Report Verification|Independent Assurance")
    pattern_institution = re.compile("HKQAA|Hong Kong Quality Assurance Authority|BSI")
    matched_pages_assurance = []
    matched_pages_institution = []
    yes_or_no = "N"
    txt_path = StringIO()

    for i in range(len(pdf.pages)):
        pdf_text = pdf.pages[i].extract_text()

        # write txt in preparation for standard keyword count
        txt_path.write(pdf_text)

        # assurance judgement (Y/N)
        if pattern_assurance.search(pdf_text):
            matched_pages_assurance.append(i)
            yes_or_no = "Y"

        # assurance institution name
        institution_name = pattern_institution.search(pdf_text)
        if institution_name:
            matched_pages_institution.append(i)

    matched_pages_assurance = ','.join(matched_pages_assurance)

    return txt_path


def standard_keyword_count(pdf) -> pd.DataFrame:
    """
    obtain the keyword counts result of a pdf globally
    :param pdf: opened pdf file data
    :return: keyword counts dataframe
    """
    txt_path = StringIO()
    for page in pdf.pages:
        text_tmp = page.extract_text()
        txt_path.write(text_tmp)
    txt = txt_path.getvalue()

    # cut words
    words = jieba.lcut(str(txt))

    # standard keyword counts
    keywords_lst = ["SASB", "GRI", "HKEX"]
    counts = [words.count(word) for word in keywords_lst]

    # arrange data format
    yes_or_no = ['Y' if i > 0 else 'N' for i in counts]  # judge value
    col = [i + '(counts)' for i in keywords_lst]  # rename cols
    val = counts.copy()
    col.extend(["SASB(Y/N)", "GRI(Y/N)", "HKEX(Y/N)"])  # add cols
    val.extend(yes_or_no)  # add judge value

    return pd.DataFrame([dict(zip(col, val))], index=[pdf_path.name])  # note pdf_path is not passed here

@st.cache
def analyse_pdf(pdf_path, df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse one pdf file
    :param pdf_path: pdf file, must be 'file-like'
    :param df: empty dataframe
    :return: dataframe with datas
    """
    # read pdf content and write it to txt
    # txt_path = StringIO()
    if pdf_path is not None:
        with pdfplumber.open(pdf_path) as pdf:
            df1 = standard_keyword_count(pdf)
        df = pd.concat([df, df1])

    return df


# some funny shows
def balloon():
    """
    show balloon callback animation
    """
    st.balloons()


st.title("Jeffery's First Streamlit")
save_df = pd.DataFrame()

# a form container
with st.form("my_form"):
    # initialize and collect data
    df = pd.DataFrame()  # initialize empty dataframe
    pdf_paths = st.file_uploader("Drag and drop pdf files here", accept_multiple_files=True)  # load pdf files
    file_name = st.text_input('Please enter the file name:', placeholder='enter something here')  # customize the name of saved excel file

    # define submit button and work flow after press the button
    submitted = st.form_submit_button("Submit")
    if submitted:
        # get analyse result table
        for pdf_path in pdf_paths:
            df = analyse_pdf(pdf_path, df)

        save_df = df[["SASB(Y/N)", "SASB(counts)", "GRI(Y/N)", "GRI(counts)", "HKEX(Y/N)", "HKEX(counts)"]]  # reorder columns
        st.dataframe(save_df)  # display the table

# download data table
if save_df.shape != (0, 0):
    # judge and revise file name
    if file_name:
        if '.' not in file_name:
            file_name += '.xlsx'
        elif file_name[-5:] != '.xlsx':
            st.warning("suffix of filename should be '.xlsx', please check your filename and retry.")
            st.stop()

    # get excel file data and save it
    df_xlsx = to_excel(save_df)
    st.download_button(label='📥 Download Current Result',
                       data=df_xlsx,
                       file_name=file_name,
                       on_click=balloon)