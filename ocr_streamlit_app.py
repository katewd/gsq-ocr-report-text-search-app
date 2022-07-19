# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 12:32:49 2021

@author: Kate Wathen-Dunn, Data Scientist, Geological Survey of Queensland (GSQ)

This code is to test the use of Streamlit as a tool to explore the OCR'd GSQ report contents.

The GSQ OCR Index was created by running my 'ocr_searchable_index_creation.py' script 
over 58,000 OCR'd reports. As more reports become open-file and are OCR'd, 
the index json file will be updated and pushed to the repository. 

"""

# import the libraries
import streamlit as st
import json
import pandas as pd
import numpy as np
from PIL import Image
import os
import re
import requests


# st.set_page_config(
#       page_title="GSQ OCRd Report Search App",
#       layout="wide",
#       initial_sidebar_state="expanded",
# )


# Build the app components

# add a title with the GSQ and Resources Dept. logo
gsq = Image.open('gsq_logo.jpg')
resources = Image.open('resources_logo.jpg')

col1, col2, col3 = st.columns([1,3,1])
with col1:
    st.image(gsq, width=100)
with col2:
    st.subheader('Geological Survey of Queensland')
with col3:
    st.image(resources, width=100)

# add title
st.header('Searchable Text Index for GSQ Reports')

# add an intro
st.write("The Geological Survey of Queensland (GSQ) is the custodian of over 100,000 reports and submissions from the Queensland resources industry, dating back more than 100 years. These legacy reports have been digitised using Optical Character Recognition (OCR) software to make them machine-readable.")
st.write('The purpose of this search capability is to find reports that contain terms of interest based on text content, across commodities and report types, and to be able to download these reports in bulk. The GSQ Open Data Portal has an API that can access the reports, including any associated documents. The reports found in the search results here can be downloaded in full via the API. With the CSV of your search results, use the [ckan_downloader_example.py](https://github.com/geological-survey-of-queensland/open-data-api/blob/master/ckan_downloader_example.py) to download your report search results in bulk')
st.markdown("This GSQ Report Index is our first version and was created from more than 58,000 open-file OCR\'d reports. As more reports become open-file in the future, the GSQ Report Index will be updated. Improvements to this app will be ongoing, please contact <GSQOpenData@resources.qld.gov.au> for app issues.")
st.markdown('Please note, the GSQ Report Index contains only **words and letters**, no numbers. If you are looking for reports on a particular permit or borehole number, the [GSQ Open Data Portal](https://geoscience.data.qld.gov.au/) is a more suitable place for your search.')
st.markdown('**A search term can be a single word, or a phrase of up to 3 words that you would expect to occur together in a sentence.**')

            

# # import the S3 OCR JSON file (stored as a string)
index_url = 'https://gsq-horizon.s3.ap-southeast-2.amazonaws.com/DATASETS/ds000079/v01_GSQ_OCR_index_single_plus_ngrams.json'


@st.experimental_memo(suppress_st_warning=True)   
def import_index():
    st.write("Cache miss -- import_index called")
    response = requests.get(index_url)
    # import the S3 OCR Index JSON file (stored as a string)
    ocr = response.json()
        # convert the json string to a dictionary
    ocr_index = json.loads(ocr)
    return ocr_index
  
ocr_index = import_index() 


# add function for converting results into CSV format
@st.cache
def convert_df(df):
    # Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')


# Add a simple search option widget
st.header('Basic Search')

# Add an advanced search radio button to search on multiple terms
advanced = st.checkbox('Advanced Search option: Use conditional joiners (and, or, not) to search for multiple terms')

###############
if "basic_submit_button" not in st.session_state:
    st.session_state.basic_submit_button = False


with st.form(key='basic_search_form'):
    basic_text_input1 = st.text_input(label='Enter the search term   (maximum of 3 consecutive words)')
    basic_submit_button = st.form_submit_button(label='Search')

if basic_submit_button or st.session_state.basic_submit_button:
    st.session_state.basic_submit_button = True
    st.markdown('*Searching the OCR\'d open-file GSQ Reports...*')
    st.write('\n')
    st.spinner(text='searching...')
    
    # Process search term to lowercase
    w01 = basic_text_input1.lower()
    
    
    # Remove numbers, symbols and punctuation
    w0 = "".join([ w if (w.isalpha() or w == " ") else "" for w in w01])
    if w01.isalpha() == False:
        st.write("Modifying search term to", w0)
        
    # lemmatise search term
    #word0 = wnl.lemmatize(w0)  # this index file not lemmatised so skip
    word0 = w0
    
    # easter egg
    if word0 == 'balloon':
        st.balloons()
    
    try:
        result0 = ocr_index[word0]
    
        
    # Create list to hold results
        search_result = []
        
        if result0:
            for item in result0:
                search_result.append(item)
            search_result.sort()
            output = ', '.join(search_result)
            st.write(len(search_result),'results found')
            if len(search_result) > 200:
                st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
            else:
                st.write('The following reports contain the term',w0,':')
                output
        
            st.write('\n')
            st.write('\n')
            
            # Convert the output to csv format
            results_df = pd.DataFrame(search_result, columns=['report_pid'])
            
            results_csv = convert_df(results_df)
            
            st.markdown('**Download the basic search results as a CSV file?**')
            
            st.download_button(
                    label='Download Report List as CSV', 
                    data=results_csv, 
                    file_name=basic_text_input1+'_'+'search_results.csv',
                    mime='text/csv')
            
            st.write('\n')
            st.write('The GSQ Open Data Portal has an API that allows access to the reports, including any associated documents. The reports found in the search results here can be downloaded in full via the API')
            st.markdown('With the CSV of your search results, use the [ckan_downloader_example.py](https://github.com/geological-survey-of-queensland/open-data-api/blob/master/ckan_downloader_example.py) to download your report search results in bulk')
            
            # st.markdown('**Download the report documents in full?**')
            # if st.button('Download full Reports'):
            #     st.write('still working on this part....')
            
            st.session_state.basic_submit_button = False
    
    except:
        KeyError()
        st.write('Sorry, the search term was not found in the GSQ reports')
        st.write('Try searching the words in a different order')
        st.write('\n')



# Add the advanced search term input widget
if advanced:
    st.header('Advanced Search')
    st.write('Each search term may be a single word or a phrase of up to 3 consecutive words that you\'d expect to occur together in a sentence)')
    st.write('Please note: The advanced search looks for \'(term1 condition1 term2) condition2 term3\'')
    with st.form(key='advanced_search_form'):
        text_input1 = st.text_input(label='Enter the first search term (term1)')
        join1 = st.selectbox('first conditional search type (condition1)',('AND', 'OR', 'NOT'))
        text_input2 = st.text_input(label='Enter the second search term (term2)')
        join2 = st.selectbox('second conditional search type (condition2)',('AND', 'OR', 'NOT'))
        text_input3 = st.text_input(label='Enter the third search term (term3)')
        advanced_submit_button = st.form_submit_button(label='Search')
    
    if advanced_submit_button:
        st.markdown('*Searching the OCR\'d open-file GSQ Reports...*')
        st.write('\n')
        st.spinner(text='searching...')
        
        # convert to blank string if no input
        text_input1 = text_input1 if text_input1 else ""
        text_input2 = text_input2 if text_input2 else ""
        text_input3 = text_input3 if text_input3 else ""
                
        
        # Process search term to lowercase
        w1 = text_input1.lower()
        w2 = text_input2.lower()
        w3 = text_input3.lower()
        
        # Remove numbers, symbols and punctuation
        w11 = "".join([w if (w.isalpha() or w == " ") else "" for w in w1])
        
        w22 = "".join([w if (w.isalpha() or w == " ") else "" for w in w2])
        
        w33 = "".join([w if (w.isalpha() or w == " ") else "" for w in w3])
        
        
        if (w1.isalpha() or w2.isalpha() or w3.isalpha()) == False:
            st.write("Modifying search term to", w11, join1, w22, join2, w33)
        
        
        # lemmatise search term       # this index not lemmatised so skip
        #word1 = wnl.lemmatize(w11)
        #word2 = wnl.lemmatize(w22)
        #word3 = wnl.lemmatize(w33)
        
        word1 = w11
        word2 = w22
        word3 = w33
        
                    
        # Create lists to hold results
        search_result = []
        final_search_result = []

        # catch the KeyError when Index doesn't contain search term
        try:

            # Check the third search term exists, then search '(term1 condition1 term2) condition2 term3'
            if text_input3 != '':
                
                result1 = ocr_index[word1]
                result2 = ocr_index[word2]
                result3 = ocr_index[word3]
                                   
                # Add AND/AND Boolean search conditions
                if (join1 == 'AND' and join2 == 'AND'):
                    for item in result2:
                        if item in result1:
                            search_result.append(item)
                    search_result.sort()
                    for item in result3:
                        if item in search_result:
                            final_search_result.append(item)
                    final_search_result.sort()
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2, join2, text_input3,':')
                        output
                        
                # Add AND/OR Boolean search conditions
                elif (join1 == 'AND' and join2 == 'OR'):
                    for item in result2:
                        if item in result1:
                            search_result.append(item)
                    for item in result3:
                        if item not in search_result:
                            search_result.append(item)
                    search_result.sort()
                    for item in search_result:
                        final_search_result.append(item)
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2, join2, text_input3,':')
                        output
                        
                # Add AND/NOT Boolean search conditions                    
                elif (join1 == 'AND' and join2 == 'NOT'):
                    for item in result2:
                        if item in result1:
                            search_result.append(item)
                    search_result.sort()
                    for item in search_result:
                        if item not in result3:
                            final_search_result.append(item)
                    final_search_result.sort()
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2, join2, text_input3,':')
                        output
     
                # Add OR/AND Boolean search conditions
                elif (join1 == 'OR' and join2 == 'AND'):
                    for item in result1:
                        search_result.append(item)
                    for item in result2:
                        if item not in result1:
                            search_result.append(item)
                    search_result.sort()
                    for item in result3:
                        if item in search_result:
                            final_search_result.append(item)
                    final_search_result.sort()
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2, join2, text_input3,':')
                        output
     
                # Add OR/OR Boolean search conditions
                elif (join1 == 'OR' and join2 == 'OR'):
                    for item in result1:
                        search_result.append(item)
                    for item in result2:
                        if item not in result1:
                            search_result.append(item)
                    for item in result3:
                        if item not in search_result:
                            search_result.append(item)
                    search_result.sort()
                    for item in search_result:
                        final_search_result.append(item)
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2, join2, text_input3,':')
                        output   
    
                # Add OR/NOT Boolean search conditions
                elif (join1 == 'OR' and join2 == 'NOT'):
                    for item in result1:
                        search_result.append(item)
                    for item in result2:
                        if item not in result1:
                            search_result.append(item)
                    for item in search_result:
                        if item not in result3:
                            final_search_result.append(item)
                    final_search_result.sort()
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2, join2, text_input3,':')
                        output
    
                # Add NOT/AND Boolean search conditions        
                elif (join1 == 'NOT' and join2 == 'AND'):
                    for item in result1:
                        if item not in result2:
                            search_result.append(item)
                    search_result.sort()
                    for item in result3:
                        if item in search_result:
                            final_search_result.append(item)
                    final_search_result.sort()
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2, join2, text_input3,':')
                        output
    
                # Add NOT/OR Boolean search conditions    
                elif (join1 == 'NOT' and join2 == 'OR'):
                    for item in result1:
                        if item not in result2:
                            search_result.append(item)
                    for item in result3:
                        if item not in search_result:
                            search_result.append(item)
                    search_result.sort()
                    for item in search_result:
                        final_search_result.append(item)
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2, join2, text_input3,':')
                        output
    
                # Add NOT/NOT Boolean search conditions
                elif (join1 == 'NOT' and join2 == 'NOT'):
                    for item in result1:
                        if item not in result2:
                            search_result.append(item)
                    search_result.sort()
                    for item in search_result:
                        if item not in result3:
                            final_search_result.append(item)
                    final_search_result.sort()
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2, join2, text_input3,':')
                        output
                
                
            # search 'term1 condition1 term2' only
            else:
                result1 = ocr_index[word1]
                result2 = ocr_index[word2]
                        
            # Add first Boolean search condition
                if join1 == 'AND':
                    for item in result2:
                        if item in result1:
                            final_search_result.append(item)
                    final_search_result.sort()
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(final_search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2,':')
                        output
    
                
                elif join1 == 'OR':
                    for item in result1:
                        final_search_result.append(item)
                    for item in result2:
                        if item not in result1:
                            final_search_result.append(item)
                    final_search_result.sort()
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(final_search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2,':')
                        output
                    
                elif join1 == 'NOT':
                    for item in result1:
                        if item not in result2:
                            final_search_result.append(item)
                    final_search_result.sort()
                    output = ', '.join(final_search_result)
                    if len(final_search_result) == 0:
                        st.write('Sorry, no results were found for that specific search')
                        st.write('You could try the search using similar words instead, or try the same words in a different order')
                        st.write('\n') 
                    else:
                        st.write(len(final_search_result),'results found')
                    if len(final_search_result) > 200:
                        st.write('The number of reports that contain your search term is too many to print them all out here. Download the full list using the button below.')
                    else:
                        st.write('The following reports contain the terms',text_input1, join1, text_input2,':')
                        output
    
                    
            st.write('\n')
            st.write('\n')
            
            
            # Convert the output to csv format
            df = pd.DataFrame(final_search_result, columns=['report_pid'])
            
            results_csv = convert_df(df)
            
            st.markdown('**Download the basic search results as a CSV file?**')
            st.download_button(
                    label='Download Report List as CSV', 
                    data=results_csv, 
                    file_name=text_input1+'_'+join1+'_'+text_input2+'_'+join2+'_'+text_input3+'_'+'search_results.csv',
                    mime='text/csv')
        
            st.write('\n')
            st.write('The GSQ Open Data Portal has an API that allows access to the reports, including any associated documents. The reports found in the search results here can be downloaded in full via the API')
            st.markdown('With the CSV of your search results, use the [ckan_downloader_example.py](https://github.com/geological-survey-of-queensland/open-data-api/blob/master/ckan_downloader_example.py) to download your report search results in bulk')
        
            # st.markdown('**Download the report documents?**')
            # if st.button('Get the full Reports'):
            #     st.write('still working on this part....')

        except:
            KeyError()
            st.write('The search term is not found in the GSQ Report Index')
            st.write('You could try the search again using similar words instead')
            st.write('\n') 


# Add a 'clear form' option
# st.write('\n')
# st.write('\n')
# clear_results = st.button('Clear search results')
# if clear_results:
#     st.write('this doesn\'t work properly yet...')
#     # Empty the lists used to hold results
#     #search_result = []
#     #final_search_result = []





