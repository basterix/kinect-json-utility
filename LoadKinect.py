#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 22:27:43 2023

@author: angelo
"""
#%% Load
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
# from mpl_toolkits.mplot3d import Axes3D

import easygui as eg##
joints={0:"PELVIS",1:"SPINE_NAVAL",2:"SPINE_CHEST",3:"NECK",4:"CLAVICLE_LEFT",5:"SHOULDER_LEFT",6:"ELBOW_LEFT",7:"WRIST_LEFT",8:"HAND_LEFT",9:"HANDTIP_LEFT",10:"THUMB_LEFT",11:"CLAVICLE_RIGHT",12:"SHOULDER_RIGHT",13:"ELBOW_RIGHT",14:"WRIST_RIGHT",15:"HAND_RIGHT",16:"HANDTIP_RIGHT",17:"THUMB_RIGHT",18:"HIP_LEFT",19:"KNEE_LEFT",20:"ANKLE_LEFT",21:"FOOT_LEFT",22:"HIP_RIGHT",23:"KNEE_RIGHT",24:"ANKLE_RIGHT",25:"FOOT_RIGHT",26:"HEAD",27:"NOSE",28:"EYE_LEFT",29:"EAR_LEFT",30:"EYE_RIGHT",31:"EAR_RIGHT"}
parents={0:"",1:0,2:1,3:2,4:2,5:4,6:5,7:6,8:7,9:8,10:7,11:2,12:11,13:12,14:13,15:14,16:15,17:14,18:0,19:18,20:19,21:20,22:0,23:22,24:23,25:24,26:3,27:26,28:26,29:26,30:26,31:26}
## File selection
fil=eg.fileopenbox(msg="Select a .json file extracted from Azure Kinect SDK - mkv recorder. You will be able to extract and save data and animated video",title="Kinect SDK data tool by Angelo Basteris",filetypes=["*.json"])
with open(fil) as json_data:
    data = json.load(json_data)
fr=pd.DataFrame(data["frames"])
## Time trimming
ts=[fr.iloc[i]["timestamp_usec"]/1000000 for i in range(fr.shape[0])]
[start_time,end_time]=eg.multenterbox("Select start and end time","Trim data",["Start time","End time"],[ts[0],ts[-1]])
fr=fr[(fr["timestamp_usec"]>=float(start_time)*1000000)&(fr["timestamp_usec"]<=float(end_time)*1000000)]
ts=[fr.iloc[i]["timestamp_usec"]/1000000 for i in range(fr.shape[0])]
selected_joints=eg.multchoicebox("Choose which joints you want to include","Joint selection",choices=joints.values(),preselect=range(32))
selected_joints=[i for i in joints.keys() if joints[i] in selected_joints]
dat={}
df=pd.DataFrame(ts)
for j in selected_joints:
    header=pd.DataFrame([joints[j]+"_X",joints[j]+"_Y",joints[j]+"_Z"]).T
    header.columns=["x","y","z"]
    dat[j]=pd.DataFrame([fr.iloc[i]["bodies"][0]["joint_positions"][j] for i in range(fr.shape[0])])
    dat[j].columns=["x","y","z"]
    dat[j]["ts"]=ts
    df=pd.concat((df,pd.concat((header,dat[j].iloc[:,:3]))),axis=1)
df.iloc[0,0]="time"
df.to_excel(fil.split(".")[0]+"_data.xlsx",index=False,header=False)
def update_graph(num):
    for j in selected_joints:
        data=dat[j].iloc[num]
        # print(num,data)
        # ax.scatter3D(data['x'], data['y'], data['z'])#, c=df['class'])
        # graph._offsets3d = (data.x, data.y, data.z)
        # title.set_text('3D Test, time={}'.format(num))
        graph[j][0].set_data(data['x'], data['z'])
        graph[j][0].set_3d_properties(-data['y'], 'z')
        title = ax.set_title("t=%.1f s"%(ts[num]))
        if parents[j] in selected_joints:
            # ax.plot([data.x,dat[parents[j]].iloc[0].x],[data.z,dat[parents[j]].iloc[0].z], [-data.y,-dat[parents[j]].iloc[0].y],"r.")
            graph[j][1][0].set_data([data.x,dat[parents[j]].iloc[num].x],[data.z,dat[parents[j]].iloc[num].z])
            graph[j][1][0].set_3d_properties([-data.y,-dat[parents[j]].iloc[num].y])
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_box_aspect((800,800,1500))
ax.view_init(0,45,0)
graph={}
for j in selected_joints:
    data=dat[j].iloc[0]
    graph[j]=ax.plot(data.x, data.z, -data.y,"r.")
    if parents[j] in selected_joints:
        graph[j].append(ax.plot([],[], [],"r",lw=3))
ani = animation.FuncAnimation(fig, update_graph, len(ts),interval=1, blit=False)
# Setting the axes properties
# ax.set_xlim3d([-500.0, 500.0])
# ax.set_xlabel('X')
# ax.set_ylim3d([-500.0, 500.0])
# ax.set_ylabel('Y')
# x.set_zlim3d([800.0, 1600.0])
# ax.set_zlabel('Z')
ani.save("scatter3d.gif")
plt.show()
