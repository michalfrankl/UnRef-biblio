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
        if len(i['data']['tags']) > 0 : # check that the tags list isn't empty
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
# DISPLAY DATA AND CHARTS

section = st.sidebar.selectbox('Sections', ('General', 'Country comparison'))

st.title('Historiography on refugees to East-Central Europe')

if (section == 'General'):
    st.text(f"Items total: {len(items)}")
    
    # stat per country
    if st.sidebar.checkbox("Show records per country", 1):
        #cstat = bibdf.groupby("country").zotero_key.nunique()
        cstat = bibdf.value_counts(subset=['country'])
        st.subheader("Records per country")
        st.write(cstat)
    
    # stat per tag
    if st.sidebar.checkbox("Show records per tag", 1):
        #tstat = bibdf.groupby("tag").zotero_key.nunique()
        tstat = bibdf.value_counts(subset=['tag'])
        #tstat.columns = ['tag', 'count']
        st.subheader("Records per tag")
        #st.table(tstat)
        st.write(tstat)

if (section == 'Country comparison'):

    # country, tags
    if st.sidebar.checkbox("Show records per country, tag", 1):
        ctags = bibdf.groupby(['country','tag']).zotero_key.nunique()
        st.subheader("Records per country, tag")
        st.write(ctags)
    
    #if st.sidebar.checkbox("Show boxplot chart", 1):
    #    st.subheader('Boxplot chart')
    #    bibdf['publication_year'] = pd.to_numeric(bibdf['publication_year'])
    #    bibc = bibdf[bibdf['country'].isin(countries)]
    #    bibc.boxplot(column='publication_year', by='country')
    #    st.pyplot()
    
    countries = st.sidebar.multiselect("Select countries", countries, countries)
    if st.sidebar.checkbox("Show scatter chart", 1):
        st.subheader('Scatter chart')
        bibdf[bibdf['country'].isin(countries)].plot(kind="scatter", y="publication_year", x="country", title="Refugee bibliography per country (scatter)")
        st.pyplot()
        
    for c in countries:
        cbib = bibdf[(bibdf.country == c)].value_counts(subset=['publication_year'], sort=False).plot(kind="bar", title=c);
        st.pyplot()