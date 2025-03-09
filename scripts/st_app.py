import pandas as pd

import matplotlib.pylab as plt
import seaborn as sns
sns.set_style("darkgrid")
sns.set_palette("dark")

from get_data import combine_data


import streamlit as st
import plotly.graph_objects as go


data_df = combine_data()

data_df.set_index('OCCUPANCY_DATE', inplace=True)
data_df['SHELTER_GROUP_LOCATION'] = [str(i)+" - "+str(j) for i,j in zip(data_df['SHELTER_GROUP'],data_df['LOCATION_NAME'])]

# Create the dropdown list to select which time series to plot
series_options = data_df['SHELTER_GROUP_LOCATION'].unique()  # Skip the 'Date' column
selected_series = st.selectbox("Select a time series to plot", series_options)

id = selected_series
data = data_df[data_df['SHELTER_GROUP_LOCATION'] == id]
data['temperature_2m_max'].fillna(0, inplace=True)

fig = go.Figure()

# Create the Plotly figure for time series data
fig = go.Figure()

fig.add_trace(go.Scatter(x=data.index, 
                         y=data['OCCUPANCY_RATE_BEDS'], 
                         mode='lines', 
                         name='Beds Occupancy Rate',
                         line=dict(color='grey',
                                   width=1)
                                   )
                         )

# Add second time series on the secondary x-axis
fig.add_trace(go.Scatter(x=data.index, 
                         y=data['temperature_2m_max'], 
                         mode='lines', 
                         name='Max Temp', 
                         line=dict(color='seagreen',
                                   width=1
                                   ),
                         yaxis='y2'))  # Assigning this trace to secondary x-axis


# Add title and labels
# Update layout to add a secondary y-axis
fig.update_layout(
    title=id,
    xaxis=dict(
        title='Date',
        rangeslider=dict(visible=True),  # Optional: Add a range slider for the x-axis
    ),
    yaxis=dict(
        title='Beds Occupancy Rate',  # Left y-axis label
    ),
    yaxis2=dict(
        title='Max Temp',  # Right y-axis label
        overlaying='y',   # Overlay the secondary y-axis on the primary one
        side='right',     # Position the secondary y-axis on the right
    ),
    template='ygridoff',  # Optional: Apply dark theme
    width=1500,  # Set the plot width in pixels
    height=500  # Set the plot height in pixels
)

# Display the plot in the Streamlit app
st.title('Toronto Shelter Occupancy Rates')
st.plotly_chart(fig, use_container_width=True)
