import streamlit as st
import string
import spacy
from spacy.language import Language
from spacy_language_detection import LanguageDetector
import pandas as pd

#def get_lang_detector(nlp, name):
#    return LanguageDetector(seed=42)

#sp = spacy.load('en_core_web_sm')
#nlp_model_lang_dect = spacy.load("en_core_web_sm")
#Language.factory("language_detector", func=get_lang_detector)
#nlp_model_lang_dect.add_pipe('language_detector', last=True)

#def get_lang_detector(nlp, name):
#    return LanguageDetector(seed=42)

#import streamlit_app as utils

def word_length(text):
  words = text.split()
  return len(words)

def lemmatise_(text):
    doc_ = sp(text)
    output = " ".join([token.lemma_ for token in doc_ if len(token.lemma_) >2])
    return output


def find_journal_information(text):
    journal_info = text[text.find(" "):]

    if 'doi' in journal_info:
        journal_info = journal_info[:journal_info.find('doi')]

    return journal_info


def find_date_initial_search(journal_info):
    # extract years and month from journal info
    if journal_info.find(" 19") != -1:
        start_point = journal_info.find(" 19")
        date_of_publication = journal_info[start_point+1:start_point+9]

        if date_of_publication[2] == "." or date_of_publication[2] == ";":
            date_of_publication = 'unknown'
        elif (len(date_of_publication) < 8) or (date_of_publication[4] != " "):
            date_of_publication = date_of_publication[0:4] + ' unk'


    elif journal_info.find(" 20") != -1:
        start_point = journal_info.find(" 20")
        date_of_publication = journal_info[start_point+1:start_point+9]

        if date_of_publication[2] == "." or date_of_publication[2] == ";":
            date_of_publication = 'unknown'
        elif (len(date_of_publication) < 8) or (date_of_publication[4] != " "):
            date_of_publication = date_of_publication[0:4] + ' unk'

    else:
        date_of_publication = 'unknown'

    if len(date_of_publication) >10: # something weird
        date_of_publication = 'unknown'

    return date_of_publication


def title_of_paper(text):
    study_name = text.translate(str.maketrans('', '', string.punctuation))
    if study_name.endswith('.'):
        study_name = study_name[:-1]
    return study_name


def find_doi(text):
    doi_start = text.find("10.")
    doi_int = text[doi_start:]

    doi_end_space = doi_int.find(" ")
    doi_end_line_break = doi_int.find("\r\n")

    if doi_end_space == '-1':
        # there is no space in doi
        doi_end = doi_end_line_break

    elif doi_end_line_break == '-1':
        # there is no line break in doi
        doi_end = doi_end_space

    else: # both space and line break occur
        # check which occurs first
        if doi_end_space < doi_end_line_break:
            doi_end = doi_end_space
        else:
            doi_end = doi_end_line_break

    doi = doi_int[:doi_end]
    doi = doi[:doi.find(" ")]

    return doi

def find_pmid(text):
    start = text.find('PMID')
    pmid_int = text[start+6:]

    if " " in pmid_int:
        #print(pmid_int, pmid_int.find(" "))
        pmid = pmid_int[:pmid_int.find(" ")]
    else:
        pmid = pmid_int

    return pmid

# not using
def check_language(text):

    # Run language model to skip non English textx
    doc_1 = nlp_model_lang_dect(text)
    language = doc_1._.language

    # what language is it
    langauge_out = language['language']


    return langauge_out

def find_text(paper):

    #find longest parapgraph, likely to be main text
    longest_paragraph_length = 0
    longest_paragraph_index = 0
    doi_ = ""
    pmid_ = ""
    # split txt file by new line
    paragraphs = paper.split('\r\n\r\n')

    for i in range(0,len(paragraphs)):

        # PMID and DOI
        if 'doi' in paragraphs[i].lower() and i >2:
            #st.write('doi found')
            doi_ = find_doi(paragraphs[i])

        if 'PMID' in paragraphs[i] and i >2:
            #st.write('pmid found')
            pmid_ = find_pmid(paragraphs[i])

        # look for longest paragraph by length, likey to be main text, skip if author name
        if len(paragraphs[i]) > longest_paragraph_length:# or 'Author information' in paragraphs[i] == False or 'Author information:' in paragraphs[i] == False:

            if 'Author information' in paragraphs[i]:
                continue


            longest_paragraph_index = i
            longest_paragraph_length = len(paragraphs[i])

            if len(paragraphs[longest_paragraph_index].split(" ")) <= 50:
                continue

    return paragraphs[longest_paragraph_index].replace('\r\n', ""), doi_, pmid_

def text_validity(text):
    words = text.split()
    if len(words) <30 or len(words) > 500:
        return "skip due to length"
    else:
        return text

def title_valid(text):
    words = text.split()
    if len(words) > 30:
        return "skip due to length"
    else:
        return text

def publish_validity(text):
    if len(text) >10:
        return "skip due to length"
    else:

        return text

def publish_weird_format(text, orig):
    if 'unknown' in text or '19:1' in text or '19:S' in text or '198-' in text:

        if ' 20' in text:

            year_info = text
            year_start = year_info.find(' 20')
            year_end = year_start + 9#len(' 2022 Apr')
            year_proper = year_info[year_start:year_end]

            return year_proper

        elif '19' in text:

            year_info = text
            year_start = year_info.find(' 19')
            year_end = year_start + 9
            year_proper = year_info[year_start:year_end]
            #text = year_proper

            return year_proper

        else:
            return orig
            pass
    else:
        return orig

st.write("# Work Health and Safety")

st.markdown(
    """
    ### Upload a txt file downloaded from Pubmed
    After searching or terms, choose save -> selection -> All results, Format -> Abstract (text)
    Upload tht file into the uploading widget below
"""
)

output_list = []
num_words = 0
number_of_texts = 0
num_records_skipped = 0

uploaded_files = st.file_uploader("Choose a .txt file", type = ['txt'])

if uploaded_files is not None:

    st.write('Download button will appear when finished')

    if uploaded_files.type == "text/plain":

        raw_text = str(uploaded_files.read(),"utf-8")

        # split papers as they are seperated by 3 empty lines
        paper_info = raw_text.split('\r\n\r\n\r\n')

        # loop over papers after they've been split
        for paper in paper_info:

            # set defualts in case of failure
            study_name = 'unknown'
            #langauge_out = 'unknown'
            journal_info  = 'unknown'
            date_of_publication  = 'unknown'
            pmid  = 'unknown'
            doi  = 'unknown'

            # split txt file by new line
            paragraphs = paper.split('\r\n\r\n')

            # Get relevant fields.
            journal_info = find_journal_information(paragraphs[0])
            study_name = title_of_paper(paragraphs[1])
            date_of_publication = find_date_initial_search(journal_info)

            find_text_outputs = find_text(paper)
            main_text = find_text_outputs[0]
            #langauge_out = check_language(main_text)
            doi =  find_text_outputs[1]
            pmid =find_text_outputs[2]

            # fasdter to save as dict and append
            paper_info = {
            'Title': study_name,
            #'Language':langauge_out,
            'Text': main_text,
            "Journal Information": journal_info,
            'Published':date_of_publication,
            'PMID':pmid,
            'DOI':doi
            }

            # append
            output_list.append(paper_info)

    # save to pandas df
    df_final = pd.DataFrame.from_dict(output_list)

    # show exmaple df
    st.write(df_final)

    # convert to json
    file = df_final.to_json()

    if file is not None:
        st.download_button(
            label="Download output as json",
            data=file,
            file_name='sample_df.json',
            mime='text/json'
        )
