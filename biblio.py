#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 22:15:20 2020

@author: Michal Frankl, frankl@mua.cas.cz
"""

import streamlit as st
import pandas as pd
import numpy as np
from pyzotero import zotero
from matplotlib import pyplot as plt
import zotero_config as zc

# -------------------------------------------------------------
# FUNCTIONS

@st.cache
def fetch_zotero():
    # Zotero UnRef bibliography
    zot = zotero.Zotero(zc.zotid, zc.zottype, zc.zotkey)
    
    zot.add_parameters(itemType='journalArticle || bookSection || book || thesis || webpage || blogPost || film || magazineArticle || document', sort='date', direction='asc')
    
    items = zot.everything(zot.collection_items('3UXBKWPF'))
    return(items)
    
def getBibDesc(i):
    desc = ""
    if 'creatorSummary' in i['meta']:
        desc = i['meta']['creatorSummary'] + ': '
    if 'title' in i['data']:
        if desc:
            desc = desc + i['data']['title']
        else:
            desc = i['data']['title']
    return desc.escape()

def getBibYear(i):
    if 'parsedDate' in i['meta']:
        y = i['meta']['parsedDate'][0:4]
        return y
    
def getBibCountryRow(i):
    found_countries = []
    bibRow = []
    if 'tags' in i['data']:
        print(len(i['data']['tags']))
        if len(i['data']['tags']) > 0 : # check that the tags list ins't empty
            for t in i['data']['tags']: # loop attaching tags to countries
                if t['tag'] in countries:
                    c = t['tag'] # set country for one or more rows
                    found_countries.append(c)
                    for tag in i['data']['tags']:
                        if tag['tag'] not in countries:
                            bibRow.append(i['key'])
                            bibRow.append(getBibYear(i))
                            bibRow.append(c)
                            bibRow.append(tag['tag'])                            
                            return(bibRow)
                    del c
            # fallback loop for cases with no countries
            if not found_countries:
                for tag in i['data']['tags']:
                    bibRow.append(i['key'])
                    bibRow.append(getBibYear(i))
                    bibRow.append('Not defined')
                    bibRow.append(tag['tag'])
                    return(bibRow)

# -------------------------------------------------------------
# LOAD AND PREPARE DATA
                    
# data_load_state = st.text('Loading data from UnRef Zotero...')
items = fetch_zotero()
# data_load_state.text("Done! (using st.cache)")

countries = ['Czechoslovakia', 'Poland', 'Austria', 'Hungary', 'Yugoslavia']
d = []
for i in items:
    if len(i['data']['tags']) > 0 :
        d.append(getBibCountryRow(i))

bibdf = pd.DataFrame(np.array(d), columns=['zotero_key', 'publication_year', 'country', 'tag']) 

# -----------------------------------------------------------
# DISPLAY CHARTS

countries = st.sidebar.multiselect("Select countries", countries, countries)

st.title('Historiography on refugees to East-Central Europe')
#st.write(len(items))
st.text(f"Items total: {len(items)}")

if st.sidebar.checkbox("Show boxplot chart", 1):
    st.subheader('Boxplot chart')
    bibdf['publication_year'] = pd.to_numeric(bibdf['publication_year'])
    bibc = bibdf[bibdf['country'].isin(countries)]
    bibc.boxplot(column='publication_year', by='country')
    st.pyplot()

if st.sidebar.checkbox("Show scatter chart"):
    st.subheader('Scatter chart')
    bibdf[bibdf['country'].isin(countries)].plot(kind="scatter", y="publication_year", x="country", title="Refugee bibliography per country (scatter)")
    st.pyplot()