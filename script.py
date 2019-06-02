from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import open3d as o3d
import matplotlib.pyplot as plt
import pyproj

def gps_to_ecef_pyproj(lon,lat, alt):
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    x, y, z = pyproj.transform(lla, ecef, lon, lat, alt, radians=False)
    return x, y, z

def main():
    point_clouds = pd.read_csv("./final_project_data/final_project_point_cloud.fuse", sep=',', header=None, names=['combined'])
    point_clouds = point_clouds['combined'].str.split(' ', expand=True).astype(np.float64)
    point_clouds.columns = ['latitude', 'longitude', 'altitude', 'intensity']
    x,y,z=gps_to_ecef_pyproj(np.array(point_clouds['longitude']),np.array(point_clouds['latitude']),np.array(point_clouds['altitude']))
    point_clouds['x']=x;point_clouds['y']=y; point_clouds['z']=z #add xyz to original df

    maxIntensity = point_clouds['intensity'].max()
    # point_clouds.drop(point_clouds[point_clouds['intensity']>50].index,inplace=True)
    # point_clouds.drop(point_clouds[point_clouds['altitude']>227].index,inplace=True)
    # point_clouds.drop(point_clouds[point_clouds['altitude']<224].index,inplace=True)
    # q0 = point_clouds['altitude'].quantile([0.25])
    # point_clouds.drop(point_clouds[point_clouds['altitude']>q0[.25]].index,inplace=True)


    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(point_clouds['x'], point_clouds['y'], point_clouds['altitude'], c=point_clouds['intensity'], vmin=0,vmax=maxIntensity)
    plt.show()
    # plt.savefig("output/image.jpg")

    export_csv = point_clouds.to_csv ('export_dataframe.csv', index=None, header=True)

if __name__ == "__main__":
    main()
