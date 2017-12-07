from bokeh.models import Grid
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
from bokeh.models import SingleIntervalTicker, LinearAxis
import datetime

#------------------------------
#plot Abila background
#------------------------------

# read in shp file
AB=shapefile.Reader("hw7/data/VAST-2014-MC3/Geospatial/Abila.shp")
x1s=[]
y1s=[]
for shape in AB.shapeRecords():
    x = [i[0] for i in shape.shape.points[:]]
    y = [i[1] for i in shape.shape.points[:]]
    x1s.append(x)
    y1s.append(y)
lsource=ColumnDataSource(dict(x1=x1s,y1=y1s))
#add  tools
tools="pan,wheel_zoom,reset,save"

# truck
# p=figure(title="Abila",tools=tools,x_axis_type='linear')
# p.multi_line(xs='x1',ys='y1',source=lsource,color='black',alpha=0.5,line_width=0.5)

# employee
p=figure(title="truck1",tools=tools,height=400,width=450)
p.image_url(x=24.8168, y=36.098, w=0.10, h=0.06, url=["http://i63.tinypic.com/20qm5qa.jpg"]) 
p.multi_line(xs='x1',ys='y1',source=lsource,color='black',alpha=1,line_width=0.6)

p1=figure(title="truck2",tools=tools,height=400,width=450)
p1.image_url(x=24.8168, y=36.098, w=0.10, h=0.06, url=["http://i63.tinypic.com/20qm5qa.jpg"]) 
p1.multi_line(xs='x1',ys='y1',source=lsource,color='black',alpha=1,line_width=0.6)

p2=figure(title="truck3",tools=tools,height=400,width=450)
p2.image_url(x=24.8168, y=36.098, w=0.10, h=0.06, url=["http://i63.tinypic.com/20qm5qa.jpg"]) 
p2.multi_line(xs='x1',ys='y1',source=lsource,color='black',alpha=1,line_width=0.6)

p3=figure(title="truck4",tools=tools,height=400,width=450)
p3.image_url(x=24.8168, y=36.098, w=0.10, h=0.06, url=["http://i63.tinypic.com/20qm5qa.jpg"]) 
p3.multi_line(xs='x1',ys='y1',source=lsource,color='black',alpha=1,line_width=0.6)

p4=figure(title="Abila5",tools=tools,height=400,width=450)
p4.image_url(x=24.8168, y=36.098, w=0.10, h=0.06, url=["http://i63.tinypic.com/20qm5qa.jpg"]) 
p4.multi_line(xs='x1',ys='y1',source=lsource,color='black',alpha=1,line_width=0.6)
#------------------------------
# data processing
#------------------------------

# read in gps information 
gps=pd.read_csv('hw7/data/VAST-2014-MC3/gps.csv')
gps=gps[gps['id']>36]
# split timestamp to day and minutes
Time=gps['Timestamp']
Time=Time.str.split(' ',1,expand=True)
Time.columns=['day','time']

# add column 'day' and 'min' in dataframe
gps['day']=Time['day']
gps['time']=Time['time']

#split date to day
# Time['date']=pd.to_datetime(Time['date'], errors='coerce')
# gps['day']=Time['date'].dt.day.astype(str).tolist()


# #split time to hour, minutes and seconds
# Time['time']=pd.to_datetime(Time['time'], errors='coerce')
# gps['hour']=Time['time'].dt.hour.astype(str).tolist()
# gps['min']=Time['time'].dt.minute.astype(str).tolist()
# gps['s']=Time['time'].dt.second.astype(str).tolist()


#------------------------------
# set up data
#------------------------------

source=ColumnDataSource(dict(x=gps[gps['id']==101]['long'],y=gps[gps['id']==101]['lat']))
source1=ColumnDataSource(dict(x=gps[gps['id']==104]['long'],y=gps[gps['id']==104]['lat']))
source2=ColumnDataSource(dict(x=gps[gps['id']==105]['long'],y=gps[gps['id']==105]['lat']))
source3=ColumnDataSource(dict(x=gps[gps['id']==106]['long'],y=gps[gps['id']==106]['lat']))
source4=ColumnDataSource(dict(x=gps[gps['id']==107]['long'],y=gps[gps['id']==107]['lat']))


#------------------------------
# set up grid unit
#------------------------------
# lat_min=min(gps['lat'])
# lat_max=max(gps['lat'])
# long_min=min(gps['long'])
# long_max=max(gps['long'])
# lat_range=lat_max-lat_min
# long_range=long_max-long_min

# i=50
# lat_int=lat_range/i
# long_int=long_range/i

# fre_ran=[0,20,70,200,500,100000]
# co=['grey','yellow','orange','red','blue']
# al=[0.5,0.5,0.5,0.5,0.5]

# def frequency(data):
#     fre=[]
#     xs=[]
#     ys=[]
#     for m in range(i):
#         for n in range(i):
#             f=data[
#                 (data['lat']>=(lat_min+m*lat_int))&
#                 (data['lat']<=(lat_min+(m+1)*lat_int))&
#                 (data['long']>=(long_min+n*long_int))&
#                 (data['long']<=(long_min+(n+1)*long_int))
#             ].count()[0]
#             fre.append(f)
        
#             y=lat_min+lat_int/2+m*lat_int
#             x=long_min+long_int/2+n*long_int
#             ys.append(y)
#             xs.append(x)

#     fre_min=min(fre)
#     fre_max=max(fre)
#     dfre=pd.DataFrame({'fre':fre})
            
#     colors=[None]*len(fre)
#     alphas=[None]*len(fre)

#     for k in range(5):
#         fre_index=dfre.index[(dfre['fre']>fre_ran[k]) & (dfre['fre']<=fre_ran[k+1])].tolist()
#         for j in fre_index:
#             colors[j]=co[k]
#             alphas[j]=al[k]
                    
    # line_colors=['black']*len(fre)
    # fre_index_0=dfre.index[(dfre['fre']>fre_ran[0]) & (dfre['fre']<=fre_ran[1])].tolist()
    # for t in fre_index_0:
    #     line_colors[t]='white'

    # source=ColumnDataSource(dict(x=xs,y=ys,color=colors,line_color=line_colors,alpha=alphas))         
    # return xs,ys,colors,alphas
    # return source



#------------------------------
#  set up control
#------------------------------

# ID_map={"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8": 8,"9":9,"10":10,"11":11,"12":12,"13":13,"14":14,"15":15,"16":16,"17": 17,"18":18,"19":19,"20":20,"21":21,"22":22,"23":23,"24":24,"25":25,"26":26,"27":27,"28": 28,"29":29,"30":30,"31":31,"32":32,"33":33,"34":34,"35":35}
# ID_select=Select(title="Car ID",options=sorted(ID_map.keys()),value="1")
# i_map={"100":100,"95":95,"90":90,"85":85,"80":80,"50":50}
# i_select=Select(title="grid unit",options=sorted(i_map.keys()),value='100')

day_map=sorted(gps['day'].unique().tolist())
day_select=Select(title="day",options=day_map,value='01/06/2014')
# max_day_select=Select(title="max day",options=day_map,value='01/19/2014')

# hour_map=sorted(gps['hour'].unique().tolist())
hour_map=['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
min_hour_select=Select(title="min hours",options=hour_map,value='0')
max_hour_select=Select(title="max hours",options=hour_map,value='23')

# min_map=sorted(gps['min'].unique().tolist())
min_map=['0','1','2','3','4','5','6','7','8','9','10',
            '11','12','13','14','15','16','17','18','19','20',
            '21','22','23','24','25','26','27','28','29','30',
            '31','32','33','34','35','36','37','38','39','40',
            '41','42','43','44','45','46','47','48','49','50',
            '51','52','53','54','55','56','57','58','59'
            ]
min_min_select=Select(title="min minutes",options=min_map,value='0')
max_min_select=Select(title="max minutes",options=min_map,value='59')

# s_map=sorted(gps['s'].unique().tolist())
s_map=min_map
min_s_select=Select(title="min seconds",options=s_map,value='0')
max_s_select=Select(title="max seconds",options=s_map,value='59')


# xs,ys,colors,alphas=frequency(ID)
# source=ColumnDataSource(dict(x=xs,y=ys,color=colors,alpha=alphas))
# source=frequency(ID)
# p1.rect(x='x',y='y',width=long_int,height=lat_int,color='color',alpha='alpha',line_color='black',source=source)
def update(attrname, old, new):
    # ID=gps[
    #     (gps['day']>=min_day_select.value)&
    #     (gps['day']<=max_day_select.value)&
    #     (pd.to_numeric(gps['hour'], errors='coerce')>=int(min_hour_select.value))&
    #     (pd.to_numeric(gps['hour'], errors='coerce')<=int(max_hour_select.value))&
    #     (pd.to_numeric(gps['min'], errors='coerce')>=int(min_min_select.value))&
    #     (pd.to_numeric(gps['min'], errors='coerce')<=int(max_min_select.value))&
    #     (pd.to_numeric(gps['s'], errors='coerce')>=int(min_s_select.value))&
    #     (pd.to_numeric(gps['s'], errors='coerce')<=int(max_s_select.value))
    # ]
    t_min=datetime.datetime(1,1,1,int(min_hour_select.value),int(min_min_select.value),int(min_s_select.value))
    t_max=datetime.datetime(1,1,1,int(max_hour_select.value),int(max_min_select.value),int(max_s_select.value))
    t_min1="{:%H:%M:%S}".format(t_min)
    t_max1="{:%H:%M:%S}".format(t_max)
    ID=gps[(gps['day']==day_select.value)&
           (gps['time']>=t_min1)&
           (gps['time']<=t_max1)
          ]
    source.data=dict(x=ID[ID['id']==101]['long'],y=ID[ID['id']==101]['lat'])
    source1.data=dict(x=ID[ID['id']==104]['long'],y=ID[ID['id']==104]['lat'])
    source2.data=dict(x=ID[ID['id']==105]['long'],y=ID[ID['id']==105]['lat'])
    source3.data=dict(x=ID[ID['id']==106]['long'],y=ID[ID['id']==106]['lat'])
    source4.data=dict(x=ID[ID['id']==107]['long'],y=ID[ID['id']==107]['lat'])
    print(1)
    # i=i_map[i_select.value]
    # lat_int=float(lat_range/i)
    # long_int=float(long_range/i)

    # min_day=pd.DataFrame({'d':[min_day_select.value]})
    # min_day=pd.to_datetime(min_day['d'], errors='coerce').dt.day.astype(str).tolist()
    
    # max_day=pd.DataFrame({'d':[max_day_select.value]})
    # max_day=pd.to_datetime(max_day['d'], errors='coerce').dt.day.astype(str).tolist()
    
    # di=(int(max_day[0])-int(min_day[0]))/14

    # hi=(pd.to_numeric(min_hour_select.value, errors='coerce')-
    #     pd.to_numeric(max_hour_select.value, errors='coerce'))/24

    # hi=(3600*(int(max_hour_select.value)-int(min_hour_select.value))+
    #     60*(int(max_min_select.value)-int(min_min_select.value))+
    #     int(max_s_select.value)-int(min_s_select.value))/(24*3600)
    

    # fre_ran=(np.array([0,20,70,200,500,100000])*di*hi).tolist()

    # xs,ys,colors,alphas=frequency(ID)
    # source.data=dict(x=xs,y=ys,color=colors,alpha=alphas)

    # source=frequency(ID)
    # print(i)
    


day_select.on_change('value',update)

min_hour_select.on_change('value',update)
max_hour_select.on_change('value',update)

min_min_select.on_change('value',update)
max_min_select.on_change('value',update)

min_s_select.on_change('value',update)
min_s_select.on_change('value',update)

# i_select.on_change('value',update)


#------------------------------
# plot routine
#------------------------------

# p1.xgrid.minor_grid_line_color = 'navy'
# p1.xgrid.minor_grid_line_alpha = 0.1
# p1.ygrid.minor_grid_line_color = 'navy'
# p1.ygrid.minor_grid_line_alpha = 0.1

# my_hover = HoverTool()
# my_hover.tooltips = [("location", "@x,@y"),("day", "@day"),("hour", "@hour"),("min", "@min"),("s", "@s"),("fre", "@fre")]
# p1.add_tools(my_hover)

p.circle(x='x',y='y',source=source,legend="truck1",size=5,color='red',alpha=0.1)
p1.circle(x='x',y='y',source=source1,legend="truck2",size=5,color='red',alpha=0.1)
p2.circle(x='x',y='y',source=source2,legend="truck3",size=5,color='red',alpha=0.1)
p3.circle(x='x',y='y',source=source3,legend="truck4",size=5,color='red',alpha=0.1)
p4.circle(x='x',y='y',source=source4,legend="truck5",size=5,color='red',alpha=0.1)

# p1.rect(x='x',y='y',width=long_int,height=lat_int,color='color',alpha='alpha',line_color=None,source=source)
layout=column(row(column(day_select,min_hour_select,min_min_select,min_s_select,max_hour_select,max_min_select,max_s_select),p,p1),row(p2,p3,p4))

# show(layout)
curdoc().add_root(layout)
# curdoc().add_root(p1)


