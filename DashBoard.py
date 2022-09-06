import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import numpy as np
import json
import plotly.graph_objects as go

features_struct=pd.read_csv("features.csv",sep='\t').T
features_struct["ones"]=np.ones(len(features_struct))
data=pd.read_csv("data.csv",sep='\t',decimal=",").fillna(0)
months=["Jan 19", "Feb 19", "Mar 19", "Apr 19", "May 19", "Jun 19"]
dates={'01/01/2019':"Jan 19", '02/01/2019':"Feb 19", '03/01/2019':"Mar 19", '04/01/2019':"Apr 19",\
       '05/01/2019':"May 19", '06/01/2019':"Jun 19"}
data.Date=data.Date.apply(lambda x:dates[x])



st.set_page_config(page_title='UNICEF DashBoard',layout="wide")

st.title("Apps for vizualisation of indicators from the UNICEF Database")

col1,col2,col3=st.columns([2,1,2])
level=col1.selectbox("Select a level of visualization",["Governorate","District","Sub-District"])
with open(level.lower()+"s.geojson") as response:
    geojson = json.load(response)
    
geo_dico={"Governorate":"ADM1_EN","District":"ADM2_EN","Sub-District":"ref"}
geokey=geo_dico[level]
category=col3.selectbox("Select a category of indicators",[i for i in features_struct[0].unique() if i!="#"])

col1.subheader("data structure of indicators in : "+category) 
features=features_struct[features_struct[0]==category].copy()
if not col3.checkbox("Hide structure"):
	#features=features.ffill(axis=1)
	fig = px.treemap(features, path=[0,1,2,3,4,5], values='ones')
	fig.update_layout(margin = dict(t=0, l=25, r=25, b=25))

	st.plotly_chart(fig,use_container_width=True)

feats=st.multiselect("Select one indicator to visualize it or several to visualize their sum",[i for i in features.ffill(axis=1)[5].unique()])

if level!="Sub-District":
	df=data[[level,"Date"]].copy()
	df["indicator"]=np.zeros(len(df))
else:
	df=data[["District",level,"Date"]].copy()
	df=df[df[level]!="Unknown"].copy()
	df.columns=["District","sd","Date"]
	df[level]=df.apply(lambda row:row["District"]+" "+row["sd"],axis=1)
	df["indicator"]=np.zeros(len(df))

for feat in feats:
	df["indicator"]+=data[feat]
	
if len(feats)>1:
	titre="Sum of the selected indicators per month"
else:
	titre="Evolution of indicator: "+" - ".join(features.ffill(axis=1)[features.ffill(axis=1)[5]==feats[0]].iloc[0].unique()[:-1])

df=df.groupby([level,"Date"]).sum().unstack().fillna(0)[[("indicator",months[i]) for i in range(6)]]
df.columns=months
df["all"]=df.sum(axis=1)


col1,col2=st.columns([3,3])

month=col1.selectbox("Select month :",["all"]+months)

carte = px.choropleth_mapbox(df, geojson=geojson, locations=df.index, color=month,
                           color_continuous_scale="Viridis",featureidkey="properties."+geokey,
                           range_color=(0, max(df[month])),
                            mapbox_style="carto-positron",
                           zoom=7, center = {"lat": 15.5, "lon": 43.6},
                           opacity=0.5, height=800
                           )
carte.update_geos(fitbounds="locations", visible=False)
carte.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

col1.plotly_chart(carte,use_container_width=True)

regions=col2.multiselect("Select some specific "+level+" (All selected by default)",df.index.tolist())
if len(regions)==0:
	regions=df.index.tolist()
fig = go.Figure()
for i in regions:
	if df.loc[i]["all"]>0:
	    fig.add_trace(go.Scatter(
        	x=months, y=df[months].loc[i],
        	hoverinfo='x+y+name',
        	mode='lines',
        	name=i,
        	stackgroup='one' # define stack group
    		))



fig.update_layout(title=titre,margin={"r": 20, "t": 50, "l": 40, "b": 20})
fig.update_layout(yaxis={'title':'Cumulative value'})
fig.update_layout(legend_title=level)                
col2.plotly_chart(fig,use_container_width=True)


if not col2.checkbox("Hide data"):
	col2.dataframe(df)

other_indicators=st.multiselect('Visualize other indicators over the same region(s)',[i for i in features_struct.ffill(axis=1)[5].unique()])

col1,col2=st.columns([3,3])

if len(other_indicators)>0:
	fig.update_layout(title="Above selected indicator")
	col1.plotly_chart(fig,use_container_width=True)
	
	for indicator in other_indicators:
		df2=data[[indicator,level,"Date"]].groupby([level,"Date"]).sum().unstack().fillna(0)[[(indicator,months[i]) for i in range(6)]]
		df2.columns=months
		df2["all"]=df2.sum(axis=1)
		
		if len(regions)==0:
			regions=df2.index.tolist()
		fig2 = go.Figure()
		for i in regions:
			if df2.loc[i]["all"]>0:
			    fig2.add_trace(go.Scatter(
				x=months, y=df2[months].loc[i],
				hoverinfo='x+y+name',
				mode='lines',
				name=i,
				stackgroup='one' # define stack group
		    		))
		fig2.update_layout(title="Evolution of indicator: "+\
		" - ".join(features_struct.ffill(axis=1)[features_struct.ffill(axis=1)[5]==indicator]\
						.iloc[0].unique()[:-1]),margin={"r": 20, "t": 50, "l": 40, "b": 20})
		fig2.update_layout(yaxis={'title':'Cumulative value'})
		fig2.update_layout(legend_title=level)        
		
		
		if other_indicators.index(indicator)%2==1:
			col1.plotly_chart(fig2,use_container_width=True)
		else:
			col2.plotly_chart(fig2,use_container_width=True)





