"""
Class: CS230--Section XXX 
Name: Alex Fayan
Description: (Give a brief description for Exercise name--See below)
I pledge that I have completed the programming assignment independently. 
I have not copied the code from a student or any source.
I have not given my code to any student.
#est.cache can help data go faster
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np



def input_switch(df_Cars, groupSelect):
    #this is what allows me to have the option to group either on the type of vehicle or
    # the reason for the accident
    filterC = ""
    if groupSelect == 'Car Type':
        filterC = 'VEHICLE1'
    elif groupSelect == 'Accident Reason':
        filterC = 'REASON'
    listItems = []
    if filterC == 'VEHICLE1':
        for e in df_Cars['VEHICLE1']:
            if e in listItems:
                continue
            else:
                listItems.append(e)
        boxSelect = st.selectbox('Which car would you like to see data for?',(listItems))
        df_Cars_F = df_Cars[(df_Cars.VEHICLE1 == boxSelect)]
        df_result = (df_Cars_F['REASON'].value_counts().rename_axis('Reasons').
                     reset_index(name='Counts'))
    elif filterC == 'REASON':
        for e in df_Cars['REASON']:
            if e in listItems:
                continue
            else:
                listItems.append(e)
        boxSelect = st.selectbox('Which car would you like to see data for?',(listItems))
        df_Cars_F = df_Cars[(df_Cars.REASON == boxSelect)]
        df_result = (df_Cars_F['VEHICLE1'].value_counts().rename_axis('Vehicle1').reset_index(name='Counts'))
    return df_result

def filter_unspec_C(df_result, unspecSelect):
    #This function graphs depending on if we want unspecified values and grouping by Car type
    if unspecSelect == 'Yes':
        df_result = df_result.drop(df_result[df_result.Reasons == 'UNSPECIFIED'].index)
        fig = px.pie(df_result,values='Counts',names='Reasons',title='Accident reasons grouped by car types')
    elif unspecSelect == 'No':
        fig = px.pie(df_result,values='Counts',names='Reasons',title='Accident reasons grouped by car types')
    return fig

def filter_unspec_A(df_result, unspecSelect):
    #This function graphs assuming you want to group by accident reason
    if unspecSelect == 'Yes':
        fig = px.pie(df_result,values='Counts',names='Vehicle1',title='Car types grouped by accident reason')
    elif unspecSelect == 'No':
        fig = px.pie(df_result,values='Counts',names='Vehicle1',title='Car types grouped by accident reason')
    return fig

def filter_size(df_result, numInput = 100):
    #this puts a minimum data size on the project to get rid of low values which cloud the pie chart
    df_result = df_result.drop(df_result[df_result.Counts < numInput].index)
    return df_result

def inj_Death(dfDanger):
    #Creates sum column on the end
    dfDanger['Injuries'] = dfDanger['PERSONS INJURED'] + dfDanger['PEDESTRIANS INJURED'] + dfDanger['CYCLISTS INJURED'] + dfDanger['MOTORISTS INJURED']
    dfDanger['Deaths'] = dfDanger['PERSONS KILLED'] + dfDanger['PEDESTRIANS KILLED'] + dfDanger['CYCLISTS KILLED'] + dfDanger['MOTORISTS KILLED']
    return dfDanger

def remove_cols(df2, listKeys):
    #Removes specific columns
    listRemove = [e for e in listKeys if e != 'Injuries' if e!= 'Deaths' if e != 'BOROUGH' if e!= 'lon' if e!='lat' if e!= 'TIME']
    df2.drop(listRemove, axis=1, inplace=True)
    return df2

def transcription_filter(dfMap):
    #Gets rid of transcription errors from data
    dfMap = dfMap.drop(dfMap[dfMap.lat < 40].index)
    dfMap = dfMap.drop(dfMap[dfMap.lon > -72].index)
    dfMap = dfMap.drop(dfMap[dfMap.lon < -74].index)
    return dfMap

def page_Home():
    st.title('NYC Crash Data Project')
    st.header("Data from crashes in NYC from 1/1/2015 to 2/28/2017")
    image1 = Image.open('nyc.jpg')
    st.image(image1,'NYC Traffic')
    st.write('Data sourced from https://www.kaggle.com/datasets/nypd/vehicle-collisions?resource=download')
    st.caption("By: Alex Fayan")



def page_Dangerous_Days():
    st.header("Dangerous Days")
    st.subheader('Show injuries and/or deaths from a range in the database')
    st.write('Range = 1/1/2015 to 2/28/2017')
    dfDanger1 = pd.read_csv('database.csv', usecols=[1,2,11,12,13,14,15,16,17,18])
    dfDanger2 = inj_Death(dfDanger1)
    date = st.text_input('Enter a date (Format MM/DD/YYYY')
    dfDanger3 = dfDanger2[(dfDanger2.DATE == date)]
    #This was something cool I wanted to do, create a graph showing how injuries and deaths progressed during the day
    #I had to first convert teh database's time entry into one I could sort on
    dfDanger3['TIME'] = dfDanger3['TIME'].str.replace(':','')
    dfDanger3['TIME'] = dfDanger3['TIME'].str.lstrip('0')
    dfDanger3['TIME'] = dfDanger3['TIME'].astype(float)
    #One all of the times were in as numbers, I could sort to organize each day
    dfDanger4 = dfDanger3.sort_values(by='TIME',ascending=True)
    st.dataframe(dfDanger4)
    type = st.radio('Filter graph on deaths or injuries',('Injuries', 'Deaths'))
    #Cum Sum allows us to show cumulative injures/deaths during the day
    dfDanger4['Injuries'] = dfDanger4['Injuries'].cumsum()
    dfDanger4['Deaths'] = dfDanger4['Deaths'].cumsum()
    if type == 'Injuries':
        line = px.line(dfDanger4,x='TIME',y='Injuries',title='Injuries at Times')
    elif type == 'Deaths':
        line = px.line(dfDanger4,x='TIME',y='Deaths',title='Injuries at Times')
    st.plotly_chart(line)
    st.caption('This graph shows us the progression of the selected option throughout the day')

    st.subheader("Showing days with the highest injuries/deaths/total")
    dfDanger = pd.read_csv('database.csv', usecols=[1,2,11,12,13,14,15,16,17,18])
    dfDanger['Injuries'] = dfDanger['PERSONS INJURED'] + dfDanger['PEDESTRIANS INJURED'] + dfDanger['CYCLISTS INJURED'] + dfDanger['MOTORISTS INJURED']
    dfDanger['Deaths'] = dfDanger['PERSONS KILLED'] + dfDanger['PEDESTRIANS KILLED'] + dfDanger['CYCLISTS KILLED'] + dfDanger['MOTORISTS KILLED']
    df2 = dfDanger.groupby(['DATE'], as_index=False).sum()
    listKeys = list(df2.columns.values)
    listRemove = [e for e in listKeys if e != 'Injuries' if e!= 'Deaths' if e!='DATE']
    df2.drop(listRemove, axis=1, inplace=True)
    boxSelect = st.radio('Which graph would you like to display?',
                             ('Highest Injuries','Highest Deaths','Highest Total'))
    if boxSelect == 'Highest Injuries':
        df3 = df2.nlargest(10,'Injuries')
        chart = px.bar(df3,x="DATE",y="Injuries", title='Highest Injury Dates')
    elif boxSelect == 'Highest Deaths':
        df3 = df2.nlargest(10,'Deaths')
        chart = px.bar(df3,x="DATE",y="Deaths", title = 'Highest Death Dates')
    elif boxSelect == 'Highest Total':
        df2['Total'] = df2['Injuries'] + df2['Deaths']
        df2.drop(['Injuries', 'Deaths'], axis=1, inplace=True)
        df3 = df2.nlargest(10,'Total')
        chart = px.bar(df3,x="DATE",y="Total", title='Highest Total Dates')
        st.dataframe(df3)
    st.plotly_chart(chart)
    st.caption('This chart shows days with the higest of each input, with the highest on the left')



def page_Distractions():
    #building this chart in particular was very difficult, there were many
    #different factors to consider and getting them all to work as desired took some time
    st.header('Showing grouped outcomes based on either car type or accident reason')
    df_Cars = pd.read_csv('database.csv', usecols=[19,24])
    df_Cars.rename(columns = {'VEHICLE 1 TYPE':'VEHICLE1','VEHICLE 1 FACTOR':'REASON'}, inplace = True)
    #I really wanted to be able to 'invert' the pie chart
    #which I did with this line and this function, thought it provided an interesting perspective
    groupSelect = st.radio('Would you like to group by car type or accident reason?',('Accident Reason','Car Type'))
    df_result = input_switch(df_Cars, groupSelect)
    st.dataframe(df_result)
    dataSelect = st.radio('Would you like to include all data or just the most common?',
              ('Most Common','All Data'))
    unspecSelect = st.radio('Would you like to remove unspecified reasons?',
              ('Yes','No'))
    #This whole if statement allows us to create different pie charts based on the inputs
    if groupSelect == 'Car Type':
        if dataSelect == 'Most Common':
            numInput = st.number_input("What would you like to filter out data below?)")
            if numInput == 0:
                df_result = filter_size(df_result)
                chart = filter_unspec_C(df_result, unspecSelect)
            elif numInput != 0:
                df_result = filter_size(df_result)
                chart = filter_unspec_C(df_result)
            chart = filter_unspec_C(df_result, unspecSelect)
        elif dataSelect == 'All Data':
            chart = filter_unspec_C(df_result, unspecSelect)
    elif groupSelect == 'Accident Reason':
        if dataSelect == 'Most Common':
            numInput = st.number_input("What would you like to filter out "
                                        "data below?")
            df_result = filter_size(df_result, numInput)
            chart = filter_unspec_A(df_result, unspecSelect)
        elif dataSelect == 'All Data':
            chart = filter_unspec_A(df_result, unspecSelect)
    st.plotly_chart(chart)
    st.caption('The pie chart shows either grouped reasons for accident or '
               'type of car involved in accident reason')

def page_Map():
    #I wanted to create maps to visualize the data
    dfMap = pd.read_csv ('database.csv', usecols=[0,5,6,18])
    dfMap.rename(columns = {'LATITUDE':'lat','LONGITUDE':'lon','MOTORISTS KILLED':'MDeaths'}, inplace = True)
    st.header('Accidents in NYC')
    st.subheader("Filter points on the map based on the deaths involved in each accident")
    dfMap = transcription_filter(dfMap)
    num = int(st.slider("Select Accident Deaths", min_value=0, max_value=3))
    dfMap = dfMap[dfMap['MDeaths'] == num]
    st.map(dfMap.dropna(subset=["lon", "lat"]))
    #given that the full city data was somewhat clustered, I wanted to add the option to filter by borough
    st.subheader('Filter information based on data from specific boroughs:')
    image1 = Image.open('boroughs.jpg')
    st.image(image1,'Map of boroughs in the city')
    boroughDF = pd.read_csv('database.csv', usecols=[0, 3, 5, 6, 11,12,13,14,15,16,17,18])
    boroughDF.rename(columns = {'LATITUDE':'lat','LONGITUDE':'lon'}, inplace = True)
    mapDFB = inj_Death(boroughDF)
    mapDFB.dropna(subset=["BOROUGH"])
    listKeys = list(mapDFB.columns.values)
    mapDFB = remove_cols(mapDFB, listKeys)
    mapDFB = transcription_filter(mapDFB)
    listOfBoroughs = []
    for e in mapDFB['BOROUGH']:
        if e in listOfBoroughs:
            continue
        else:
            listOfBoroughs.append(e)
    borough = st.selectbox('Choose a borough: ',(listOfBoroughs))
    secondOption = st.radio('Would you like to filter on injuries/deaths?',('No',"Yes"))
    if secondOption == 'No':
        newdf = mapDFB[(mapDFB.BOROUGH == borough)]
        st.map(newdf.dropna(subset=['lon','lat']))
    elif secondOption == 'Yes':
        radioF = st.radio('Choose to look at non-injuries or injuries: ',('Non-Injuries','Injuries','Deaths'))
        if radioF == 'Non-Injuries':
            newdf = mapDFB[(mapDFB.BOROUGH == borough) & (mapDFB.Injuries == 0)]
            st.map(newdf.dropna(subset=['lon','lat']))
        elif radioF == 'Injuries':
            newdf = mapDFB[(mapDFB.BOROUGH == borough) & (mapDFB.Injuries != 0)]
            st.map(newdf.dropna(subset=['lon','lat']))
        elif radioF == 'Deaths':
            newdf = mapDFB[(mapDFB.BOROUGH == borough) & (mapDFB.Deaths != 0)]
            st.map(newdf.dropna(subset=['lon','lat']))

def main():
    page = st.sidebar.selectbox('Select a page to view',('Home','Dangerous Days','Distractions','Map'))
    if page == "Home":
        page_Home()
    if page == 'Dangerous Days':
        page_Dangerous_Days()
    elif page == 'Distractions':
        page_Distractions()
    elif page == 'Map':
        page_Map()

main()
