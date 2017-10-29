import numpy as np
import pandas as pd
import io
from bokeh.plotting import figure, save,output_file
from bokeh.layouts import widgetbox, row, column, layout
from bokeh.models import ColumnDataSource, Select, Slider,HoverTool,LogColorMapper
from bokeh.palettes import RdYlBu11 as palette
from bokeh.io import output_notebook, show, curdoc


# read in data
# fpath = './data/costco/export_dashboard_cost_2016_06_15_12_24_55.xlsx'
fpath = 'export_dashboard_cost_2016_06_15_12_24_55.xlsx'
df = pd.read_excel(fpath, sheetname='Country List')
df.head()


# read data in ColumnDataSource
Latitude=df['Latitude']
Longitude=df['Longitude']
Keyword_Repetitions=df['Keyword Repetitions']
Country=df['Country']
source=ColumnDataSource(data=dict(x=Longitude,y=Latitude,Coun=Country,Keyword_Repetitions=Keyword_Repetitions))


# set up colors using color_mapper
palette=palette
color_mapper=LogColorMapper(palette=palette)


#add  tools
tools="pan,wheel_zoom,reset,save"
p=figure(title="Twitter Geolocalization Interactive Plot",tools=tools,x_axis_location=None, y_axis_location=None)
p.grid.grid_line_color = None
p.circle(x=Longitude,y=Latitude,size=Keyword_Repetitions/5,color="red")
#add hover
my_hover = HoverTool()
my_hover.tooltips = [("Address of the point", "@x,@y")]
p.add_tools(my_hover)
curdoc().add_root(p)


# need to slove
# county_xs = [county["lons"] for county in counties.values()]？？？
# county_ys = [county["lats"] for county in counties.values()]??

# p.patches('x', 'y',source=source,fill_color={'field':'Country','transform':color_mapper},
#           fill_alpha=10, line_color="white", line_width=1)
# show(p)