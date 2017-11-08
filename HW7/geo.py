
# coding: utf-8

# In[14]:


import numpy as np
import pandas as pd
import shapefile
import geopandas as gpd
from bokeh.plotting import figure,save,show
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper,Select
from bokeh.palettes import RdYlBu11 as palette
from bokeh.models import LogColorMapper
import matplotlib.pyplot as plt
from bokeh.io import output_notebook,output_file,curdoc
from bokeh.models import GeoJSONDataSource
from bokeh.layouts import layout, widgetbox,row,column

# In[18]:


# SR=shapefile.Reader("Kronos_Island.shp")
# feature=SR.shapeRecords()[0]
# first=feature.shape.__geo_interface__  
# # print (first)
# plt.figure()
# for shape in SR.shapeRecords():
#     x = [i[0] for i in shape.shape.points[:]]
#     y = [i[1] for i in shape.shape.points[:]]
#     plt.plot(x,y)
# plt.show()


# In[19]:


def getPolyCoords(row, geom, coord_type):
    """Returns the coordinates ('x' or 'y') of edges of a Polygon exterior"""

    # Parse the exterior of the coordinate
    exterior = row[geom].exterior

    if coord_type == 'x':
        # Get the x coordinates of the exterior
        return list( exterior.coords.xy[0] )
    elif coord_type == 'y':
        # Get the y coordinates of the exterior
        return list( exterior.coords.xy[1] )


# In[21]:


KI=gpd.read_file("Kronos_Island.shp")
KI['x'] = KI.apply(getPolyCoords, geom='geometry', coord_type='x', axis=1)
KI['y'] = KI.apply(getPolyCoords, geom='geometry', coord_type='y', axis=1)
KIsource=GeoJSONDataSource(geojson=KI.to_json())
color_mapper=LogColorMapper(palette=palette)
#add  tools
tools="pan,wheel_zoom,reset,save"
p=figure(title="Kronos_Island",tools=tools)
# p.grid.grid_line_color = None
p.patches('x','y',source=KIsource,fill_color='white',line_color="black", line_width=1)
# show(p)



# In[23]:


AB=shapefile.Reader("Abila.shp")
x1s=[]
y1s=[]
x2s=[]
y2s=[]
for shape in AB.shapeRecords():
    if len(shape.shape.points)>1:
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        x1s.append(x)
        y1s.append(y)
    else:
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        x2s.append(x)
        y2s.append(y)
x2s=np.array(x2s).ravel().tolist()
y2s=np.array(y2s).ravel().tolist()
lsource=ColumnDataSource(dict(x1=x1s,y1=y1s))
psource=ColumnDataSource(dict(x2=x2s,y2=y2s))
p1=figure(title="Abila")
p1.circle(x='x2',y='y2',source=psource,color='black',size=3)
p1.multi_line(xs='x1',ys='y1',source=lsource,color='black',line_width=1)
# my_hover = HoverTool()
# my_hover.tooltips = [("location", "@x2,@y2")]
# p1.add_tools(my_hover)
# show(p1)
gps=pd.read_csv('gps.csv')
ID_map={"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8": 8,"9":9,"10":10,"11":11,"12":12,"13":13,"14":14,"15":15,"16":16,"17": 17,"18":18,"19":19,"20":20,"21":21,"22":22,"23":23,"24":24,"25":25,"26":26,"27":27,"28": 28,"29":29,"30":30,"31":31,"32":32,"33":33,"34":34,"35":35}
ID_select=Select(title="Car ID",options=sorted(ID_map.keys()),value="1")
ID=gps.loc[gps['id']==1]
source=ColumnDataSource(dict(x=ID['long'],y=ID['lat'],Time=ID['Timestamp']))


def update(attrname, old, new):
    car_id=ID_map[ID_select.value]
    # print(car_id)
    ID=gps.loc[gps['id']==car_id]
    # print(ID)
    source.data=dict(x=ID['long'],y=ID['lat'],Time=ID['Timestamp'])
    # p1.circle(x='x',y='y',source=source,size=1,color='red')
ID_select.on_change('value',update)
p1.circle(x='x',y='y',source=source,size=1,color='red')
my_hover = HoverTool()
my_hover.tooltips = [("location", "@x,@y"),("Time","@Time")]
p1.add_tools(my_hover)

layout=column(ID_select,p1)
# show(layout)
curdoc().add_root(column(p,layout))

