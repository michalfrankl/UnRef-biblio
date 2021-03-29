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
import altair as alt

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


def getItemsTags(items):
    itags = []
    for i in items:
        if len(i['data']['tags']) > 0 :
            #itemtags = []
            for tag in i['data']['tags']:
                tagrow = []
                tagrow.append(i['key'])
                tagrow.append(getBibYear(i))
                tagrow.append(tag['tag'])
                itags.append(tagrow)
    return(itags)

# -------------------------------------------------------------
# LOAD AND PREPARE DATA
                    
# data_load_state = st.text('Loading data from UnRef Zotero...')
items = fetch_zotero()
# data_load_state.text("Done! (using st.cache)")

countries = ['Czechoslovakia', 'Poland', 'Austria', 'Hungary', 'Yugoslavia']
categories = ['country of refuge', 'event', 'organization', 'keyword', 'location', 'personality', 'refugee group (by ethnicity)', 'refugee group (by reason of refuge)', 'refugee group (by region/country of origin)', 'refugee group (type)', 'state actor involved']

itags = getItemsTags(items)
# print(len(itags))
tagsdf = pd.DataFrame(np.array(itags), columns=['zotero_key', 'publication_year', 'tag']) 

tagsmaster = pd.read_csv('UnRef_tags.csv')
tagsm = pd.merge(tagsdf, tagsmaster, how='left', left_on='tag', right_on='Tag')



# -----------------------------------------------------------
# DISPLAY DATA AND CHARTS

st.sidebar.title('Historiography on refugees to East-Central Europe')
st.sidebar.text(f"Items total: {len(items)}")

section = st.sidebar.selectbox('Sections', ('General', 'Country comparison', 'Tags', 'Comparison'))

if (section == 'General'): 
    
    # stat per country
    if st.sidebar.checkbox("Show records per country", 1):
        cstat = tagsm[tagsm.Category=='country of refuge'].value_counts(subset=['tag'])
        cstat = cstat.reset_index()
        cstat.columns = ['Country of refuge', 'Number of records']
        st.subheader("Records per country")
        st.write(cstat)
        
        c = alt.Chart(cstat).mark_bar().encode(x='Country of refuge', y='Number of records', size='Number of records', color='Number of records')
        st.altair_chart(c, use_container_width=True)

if (section == 'Country comparison'):
    
    #if st.sidebar.checkbox("Show boxplot chart", 1):
    #    st.subheader('Boxplot chart')
    #    bibdf['publication_year'] = pd.to_numeric(bibdf['publication_year'])
    #    bibc = bibdf[bibdf['country'].isin(countries)]
    #    bibc.boxplot(column='publication_year', by='country')
    #    st.pyplot()
    
    countries = st.sidebar.multiselect("Select countries", countries, countries)
        
    for c in countries:
        cbib = tagsm[(tagsm.tag == c) & (tagsm.Category == 'country of refuge')].value_counts(subset=['publication_year'], sort=False).reset_index()
        cbib.columns = ['Publication year', 'Number per year']
        st.subheader(c)
        c = alt.Chart(cbib).mark_bar().encode(x='Publication year', y='Number per year', size='Number per year', color='Number per year')
        st.altair_chart(c, use_container_width=True)
        
#    if st.sidebar.checkbox("Show scatter chart", 1):
#        #st.subheader('Scatter chart')
#        bibdf[bibdf['country'].isin(countries)].plot(kind="scatter", y="publication_year", x="country", title="Refugee bibliography per country (scatter)")
#        st.pyplot()

        
if (section == 'Tags'):
    
    # stat per tag
    if st.sidebar.checkbox("Show records per tag", 1):
        cat = st.sidebar.multiselect("Select tag categories", categories, categories)
        tstat = tagsm[tagsm['Category'].isin(cat)].value_counts(subset=['tag'])
        tstat = tstat.reset_index()
        tstat.columns = ['Tag', 'Number of records']
        st.subheader("Records per tag")
        st.write(tstat)
        
    # items with no tags
    if st.sidebar.checkbox("Show records without tags", 0):
        st.subheader("Records without tags")
        for i2 in items:
            if len(i2['data']['tags']) == 0:
                st.write("[" + i2['data']['title'] + "](https://www.zotero.org/groups/2363703/unlikely_refuge/collections/3UXBKWPF/items/" + i2['data']['key'] + "/collection)")
   	
if (section == 'Comparison'):
    comp1 = st.sidebar.selectbox("Select first category", categories)
    comp2 = st.sidebar.selectbox("Select second category", categories)
    
    if comp1 != comp2:
        st.subheader("Comparison of tag categories")
        # compare two categories
        tagsc = tagsm[tagsm.Category==comp1]
        tagsk = tagsm[tagsm.Category==comp2]

        comp = pd.merge(tagsc, tagsk, how='outer', on='zotero_key')

        stat = comp.value_counts(subset=['Tag_x', 'Tag_y'])
        stat = stat.reset_index()
        stat.columns = [comp1, comp2, 'Number of records']
        st.write(stat)
