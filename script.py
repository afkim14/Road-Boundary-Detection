import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyproj

def get_camera_conifg():
   with open('./final_project_data/image/camera.config', 'r') as config_file:
       config_file.readline()
       config_params = config_file.readline()
       config_params_split = config_params.split(',')
       cam_lat = float(config_params_split[0])
       cam_lon = float(config_params_split[1])
       cam_alt = float(config_params_split[2])
       cam_qs = float(config_params_split[3])
       cam_qx = float(config_params_split[4])
       cam_qy = float(config_params_split[5])
       cam_qz = float(config_params_split[6])
       return cam_lat, cam_lon, cam_alt, cam_qs, cam_qx, cam_qy, cam_qz

def filter_data(point_clouds_cp,cam_alt,delY, heightcar):
   point_clouds_cp.drop(point_clouds_cp[point_clouds_cp['altitude']>cam_alt+ delY/2-heightcar].index,inplace=True)
   point_clouds_cp.drop(point_clouds_cp[point_clouds_cp['altitude']<cam_alt- delY/2-heightcar].index,inplace=True)
   point_clouds_cp.drop(point_clouds_cp[point_clouds_cp['intensity']<50].index,inplace=True)
   return point_clouds_cp

def main():
   # pull in data
   print('Starting..')
   point_clouds = pd.read_csv("./final_project_data/final_project_point_cloud.fuse", sep=',', header=None, names=['combined'])
   point_clouds = point_clouds['combined'].str.split(' ', expand=True).astype(np.float64)
   point_clouds.columns = ['latitude', 'longitude', 'altitude', 'intensity']

   # get camera altitude, search for points nearest to camera altitude given an assumed delY height and car hegiht
   delY=2; heightcar=3
   cam_lat, cam_lon, cam_alt, cam_qs, cam_qx, cam_qy, cam_qz=get_camera_conifg()
   point_clouds_cp=filter_data(point_clouds,cam_alt,delY, heightcar)

   #make 3d plot and 2d plot
   from mpl_toolkits.mplot3d import Axes3D
   fig = plt.figure()
   ax = fig.add_subplot(111, projection='3d')
   plt.scatter(x=point_clouds_cp['longitude'],y=point_clouds_cp['latitude'],zs=point_clouds_cp['altitude'],c=point_clouds_cp['intensity'],s=0.1,vmin=20,vmax=100)
   plt.savefig('./output/3dplot.png')
   fig = plt.figure()
   plt.scatter(x=point_clouds_cp['longitude'],y=point_clouds_cp['latitude'],c=point_clouds_cp['altitude'],s=.1)
   plt.colorbar()
   plt.savefig('./output/2dplot.png')
   print('Saving figure...')
   #do clustering

if __name__ == "__main__":
   main()
