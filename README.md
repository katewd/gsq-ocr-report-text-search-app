# gsq-ocr-report-text-search-app
Code to enable text searching of OCRd GSQ open-file reports using the Streamlit app
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/katewd/gsq-ocr-report-text-search-app/main/ocr_streamlit_app.py)

## Methods
The GSQ Report Index was generated using a custom python script to capture the unique words and frequent word pairs/triples found in each of the GSQ open-file reports that had undergone optical character recognition (OCR) using the 'Wondershare PDFElement Pro' software. Many of the reports were initially stored digitally as image files, and the presence of hand-written notes, type-written fonts, stamps and stains complicated the process. Given the age and condition of some of the reports, the OCR process will not be a perfect reflection of all report contents. 
For this reason, OCR artifacts were filtered out of the results using a custom dictionary that included a full English dictionary, an expanded geological dictionary and GSQ's own Vocabularies and Organisations contents. This filtering process also excluded numbers, so please note that the search function will only return words and letters. 
Frequent word pairs/triples in the reports were filtered by frequency, so some genuine word pairs may have been excluded in this Index.
At this stage, only 58000 reports have undergone OCR and have been included in this Index. As more reports are processed, this Index will be updated.
Future versions will also include an expanded dictionary in the filtering process, so will include more possible search terms.
