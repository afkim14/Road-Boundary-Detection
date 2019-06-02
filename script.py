import numpy as np
import pandas as pd

def main():
    point_clouds = pd.read_csv("./final_project_data/final_project_point_cloud.fuse", sep=',', header=None, names=['combined'])
    point_clouds = point_clouds['combined'].str.split(' ', expand=True).astype(np.float64)
    point_clouds.columns = ['latitude', 'longitude', 'altitude', 'intensity']
    export_csv = point_clouds.to_csv ('export_dataframe.csv', index=None, header=True)

if __name__ == "__main__":
    main()
