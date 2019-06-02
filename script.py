import numpy as np
import pandas as pd
import open3d as o3d
import matplotlib.pyplot as plt
import pyproj

def gps_to_ecef_pyproj(lat, lon, alt):
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    x, y, z = pyproj.transform(lla, ecef, lon, lat, alt, radians=False)
    return x, y, z

def main():
    point_clouds = pd.read_csv("./final_project_data/final_project_point_cloud.fuse", sep=',', header=None, names=['combined'])
    point_clouds = point_clouds['combined'].str.split(' ', expand=True).astype(np.float64)
    point_clouds.columns = ['latitude', 'longitude', 'altitude', 'intensity']

    # TRANSFORM FROM POINT CLOUD (LAT LONG ALT) TO POINT CLOUD (X Y Z) using gps_to_ecef_pyproj

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


    fig = plt.figure(figsize=(30, 30))
    plt.plot(point_clouds['latitude'].tolist(), point_clouds['longitude'].tolist(), '.', color='k')
    plt.axis('off')
    fig.savefig("output/image.jpg", bbox_inches='tight')

    # export_csv = point_clouds.to_csv ('export_dataframe.csv', index=None, header=True)

if __name__ == "__main__":
    main()
