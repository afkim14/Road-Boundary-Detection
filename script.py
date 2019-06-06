import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyproj
import sys

from sklearn.cluster import DBSCAN
from collections import Counter

def gps_to_ecef_pyproj(lat, lon, alt):
   ecef = pyproj.Proj(proj="geocent", ellps="WGS84", datum="WGS84")
   lla = pyproj.Proj(proj="latlong", ellps="WGS84", datum="WGS84")
   x, y, z = pyproj.transform(lla, ecef, lon, lat, alt, radians=False)
   return x, y, z

def get_camera_conifg(camera_config_file):
   with open(camera_config_file, 'r') as config_file:
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

def filter_data_lower(point_clouds_cp,cam_alt,delY, heightcar):
    point_clouds_cp.drop(point_clouds_cp[point_clouds_cp['altitude']>cam_alt+ delY/2-heightcar].index,inplace=True)
    point_clouds_cp.drop(point_clouds_cp[point_clouds_cp['altitude']<cam_alt- delY/2-heightcar].index,inplace=True)
    point_clouds_cp.drop(point_clouds_cp[point_clouds_cp['intensity']<50].index,inplace=True)
    return point_clouds_cp

def filter_data_upper(point_clouds_cp,cam_alt,delY, heightcar):
    point_clouds_cp.drop(point_clouds_cp[point_clouds_cp['altitude']>cam_alt+ delY/2-heightcar+1.25].index,inplace=True)
    point_clouds_cp.drop(point_clouds_cp[point_clouds_cp['altitude']<cam_alt- delY/2-heightcar+2].index,inplace=True)
    return point_clouds_cp

def DBSCAN_cluster(point_clouds_cp):
    clusters = DBSCAN(eps=0.0000005).fit(point_clouds_cp)
    df = pd.DataFrame([point_clouds_cp['longitude'], point_clouds_cp['latitude'], clusters.labels_]).T
    df.columns = ['x', 'y','label'];
    max_label = df.label.mode()[0];
    max_cluster = df[df['label']==max_label];

    np_chunk = np.array(max_cluster)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.grid(True,linestyle='-',color='0.75')
    c = [1]*len(np_chunk[:,0])
    ax.scatter(np_chunk[:,0], np_chunk[:,1], c=c, s=1, edgecolors='none')
    plt.show()

def main(fuse_file, camera_config_file):
   # pull in data
   print('Starting..')
   point_clouds = pd.read_csv(fuse_file, sep=',', header=None, names=['combined'])
   point_clouds = point_clouds['combined'].str.split(' ', expand=True).astype(np.float64)
   point_clouds.columns = ['latitude', 'longitude', 'altitude', 'intensity']

   x,y,z=gps_to_ecef_pyproj(np.array(point_clouds['longitude']),np.array(point_clouds['latitude']),np.array(point_clouds['altitude']))
   point_clouds['x']=x;point_clouds['y']=y; point_clouds['z']=z #add xyz to original df

   # get camera altitude, search for points nearest to camera altitude given an assumed delY height and car hegiht
   delY=2; heightcar=3
   cam_lat, cam_lon, cam_alt, cam_qs, cam_qx, cam_qy, cam_qz=get_camera_conifg(camera_config_file)
   upper_point_clouds = point_clouds.copy(deep="true")
   point_clouds_cp=filter_data_lower(point_clouds,cam_alt,delY, heightcar)
   point_clouds_cp["level"] = "lower";
   point_clouds_cp_upper=filter_data_upper(upper_point_clouds,cam_alt,delY, heightcar)
   point_clouds_cp_upper["level"] = "upper";

   point_clouds_cp = point_clouds_cp.append(point_clouds_cp_upper)
   point_clouds_cp["x_rounded"] = np.rint(point_clouds_cp["x"] * 50)
   point_clouds_cp["y_rounded"] = np.rint(point_clouds_cp["y"] * 50)
   duplicate_point_clouds = point_clouds_cp[point_clouds_cp.duplicated(['x_rounded', 'y_rounded'])]
   duplicate_point_clouds.drop(duplicate_point_clouds[duplicate_point_clouds["level"] == "lower"].index,inplace=True);

   bottom_pc = filter_data_lower(point_clouds,cam_alt,delY, heightcar);

   bottom_pc["x_rounded"] = np.rint(bottom_pc["x"])
   bottom_pc["y_rounded"] = np.rint(bottom_pc["y"])
   second_append_pc = bottom_pc.append(duplicate_point_clouds)
   second_duplicate_pc = second_append_pc[second_append_pc.duplicated(['x_rounded', 'y_rounded'])]
   second_duplicate_pc.drop(second_duplicate_pc[second_duplicate_pc["level"] == "upper"].index,inplace=True);

   guard_rail_data = duplicate_point_clouds.sample(n=2000)
   road_data = second_duplicate_pc.sample(n=2000)

   duplicate_pc_max = guard_rail_data["intensity"].max();
   second_duplicate_pc_max = road_data["intensity"].max();

   #make 3d plot and 2d plot
   from mpl_toolkits.mplot3d import Axes3D
   fig = plt.figure()
   ax = fig.add_subplot(111, projection='3d')
   ax.set_yticklabels([])
   ax.set_xticklabels([])
   plt.scatter(x=guard_rail_data['longitude'],y=guard_rail_data['latitude'],zs=guard_rail_data['altitude'],c=guard_rail_data['intensity'],s=0.5,vmin=0,vmax=duplicate_pc_max)
   plt.scatter(x=road_data['longitude'],y=road_data['latitude'],zs=road_data['altitude'],c=road_data['intensity'],s=0.5,vmin=0,vmax=second_duplicate_pc_max)
   plt.savefig('./output/3dplot.png')
   plt.title("Guard rails on Top of Lane Marks")
   plt.ylabel("Latitude")
   plt.xlabel("Longitude")
   # plt.show()

   fig = plt.figure()
   plt.scatter(x=guard_rail_data['longitude'],y=guard_rail_data['latitude'],c=guard_rail_data['altitude'],s=.1)
   plt.colorbar()
   plt.savefig('./output/2dplot.png')
   print('Saving figure...')

   all_data = duplicate_point_clouds.append(second_duplicate_pc)
   export_csv = all_data.to_csv ('guard_rail_data.csv', index=None, header=True)

   #do clustering
   # DBSCAN_cluster(point_clouds_cp)

if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print("Please supply the point cloud data and the camera config file. Usage: python3 script.py [.fuse] [.config]")
        exit(0)
    main(sys.argv[1], sys.argv[2])
