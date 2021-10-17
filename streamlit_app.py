import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.express as px
import streamlit.components.v1 as components


@st.cache
def get_data():
	data = pd.read_parquet('data/filtered_data.parquet')
	return data

indicator_column_names = {
	'Enrollment Rate (%)': 'Adjusted net enrolment rate, primary, {} (%)',
	'Adult Literacy Rate (%)': 'Adult literacy rate, population 15+ years, {} (%)',
	'Early School Leavers': 'Early school leavers from primary education, {} (number)',
	'Gross Enrollment Rate, Primary (%)': 'Gross enrolment ratio, primary, {} (%)',
}


if __name__ == '__main__':
	data = get_data()
	filtered_data = data[data.columns.tolist()[:4] + [str(i) for i in range(2000, 2011)]].dropna(axis=0)
	
	header_container = st.container()
	display_container = st.container()

	with header_container:

		st.title("Gender Disparity in Education")
		st.markdown("____")
		st.subheader("Configuration")
		col1, col2= st.columns(2)	
		indicator_options = ['Enrollment Rate (%)', 'Adult Literacy Rate (%)', 'Early School Leavers', 'Gross Enrollment Rate, Primary (%)']
		indicator = col1.selectbox('Select Statistic: ', indicator_options)

		year = str(col1.slider('Select Year: ', min_value=2000, max_value=2010))
		col2.subheader(" ")
		show_legend = col2.checkbox(label='Show legend of Country/Category')
		st.markdown("____")
		st.subheader("Output")


	
	with display_container:

		indicator_name_male = indicator_column_names[indicator].format('male')
		indicator_name_female = indicator_column_names[indicator].format('female')

		countries_1 = set(data[data['Indicator Name']==indicator_name_male]['Country Name'].unique().tolist())
		countries_2 = set(data[data['Indicator Name']==indicator_name_female]['Country Name'].unique().tolist())
		countries = list(countries_1.intersection(countries_2))
		

		d = data[(data['Indicator Name'].isin([indicator_name_female, indicator_name_male])) & (data['Country Name'].isin(countries))][['Country Name', 'Indicator Name', year]]
		d = pd.pivot_table(d, index='Country Name', columns='Indicator Name', values=year).reset_index()
		d.rename(columns={'Country Name': 'Country', indicator_name_male: 'Male', indicator_name_female: 'Female'}, inplace=True)
		d['Difference'] = d['Male'] - d['Female']
		d.loc[d['Difference']<0, 'Difference'] = 0
		
		if show_legend:
			fig = px.scatter(
			    data_frame=d, 
			    x='Male', 
			    y='Female', 
			    color='Country',
			    size='Difference',
			    custom_data=['Country', 'Difference']
			)
		else:
			fig = px.scatter(
			    data_frame=d, 
			    x='Male', 
			    y='Female', 
			    # color='Country',
			    size='Difference',
			    custom_data=['Country', 'Difference']
			)

		fig.update_traces(
		    hovertemplate="<br>".join([
		        "Male: %{x:.2f}",
		        "Female: %{y:.2f}",
		        "Country/Category: %{customdata[0]}",
		        "Gender Disparity: %{customdata[1]:.2f}",
		    ])
		)

		fig.update_layout({
		'plot_bgcolor': 'rgba(255, 0, 0, 0.1)',
		'paper_bgcolor': 'rgba(0, 100, 200, 0.1)',
		})
		fig.update_xaxes(showgrid=False)

		display_container.plotly_chart(fig)
		st.markdown("____")