# suppress annoying pandas openpyxl warning
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import numpy as np
import fiona
from shapely.geometry import Point, LineString, shape, asLineString, mapping
from shapely import affinity
from shapely.ops import cascaded_union, transform
from functools import partial
import mpl_toolkits.basemap.pyproj as pyproj
import pandas as pd
import shutil
import GISio

def projectdf(df, projection1, projection2):
    '''
    ``df``: (dataframe) containing "geometry" column of shapely geometries
    ``projection1``: (string) Proj4 string specifying source projection
    ``projection2``: (string) Proj4 string specifying destination projection
    '''
    
    # define projections
    pr1 = pyproj.Proj(projection1)
    pr2 = pyproj.Proj(projection2)
    
    # projection function
    # (see http://toblerity.org/shapely/shapely.html#module-shapely.ops)
    project = partial(pyproj.transform, pr1, pr2)

    # do the transformation!
    newgeo = [transform(project, g) for g in df.geometry]

    return newgeo


def dissolve(inshp, outshp, dissolve_attribute):
    df = GISio.shp2df(shp, geometry=True)
    
    df_out = dissolve_df(df, dissolve_attribute)
    
    # write dissolved polygons to new shapefile
    GISio.df2shp(df_out, outshp, 'geometry', inshp[:-4]+'.prj')


def dissolve_df(in_df, dissolve_attribute):
    
    print "dissolving DataFrame on {}".format(dissolve_attribute)
    # unique attributes on which to make the dissolve
    dissolved_items = list(np.unique(in_df[dissolve_attribute]))
    
    # go through unique attributes, combine the geometries, and populate new DataFrame
    df_out = pd.DataFrame()
    length = len(dissolved_items)
    knt = 0
    for item in dissolved_items:
        df_item = in_df[in_df[dissolve_attribute] == item]
        geometries = list(df_item.geometry)
        dissolved = cascaded_union(geometries)
        dict = {dissolve_attribute: item, 'geometry': dissolved}
        df_out = df_out.append(dict, ignore_index=True)
        knt +=1
        print '\r{:d}%'.format(100*knt/length)
        
    return df_out


def join_csv2shp(shapefile, shp_joinfield, csvfile, csv_joinfield, out_shapefile, how='outer'):
    '''
    add attribute information to shapefile from csv file
    shapefile: shapefile to add attributes to
    shp_joinfield: attribute name in shapefile on which to make join
    csvfile: csv file with information to be added to shapefile
    csv_joinfield: column in csv with entries matching those in shp_joinfield
    out_shapefile: output; original shapefile is not modified
    type: pandas join type; see http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.join.html
    '''

    shpdf = GISio.shp2df(shapefile, index=shp_joinfield, geometry=True)

    csvdf = pd.read_csv(csvfile, index_col=csv_joinfield)

    print 'joining to {}...'.format(csvfile)
    joined = shpdf.join(csvdf, how='inner', lsuffix='L', rsuffix='R')

    # write to shapefile
    GISio.df2shp(joined, out_shapefile, 'geometry', shapefile[:-4]+'.prj')


def rotate_coords(coords, rot, origin):
    """
    Rotates a set of coordinates (wrapper for shapely)
    coords: sequence point tuples (x, y)
    """
    ur = LineString(unrotated)
    r = affinity.rotate(ur, rot, origin=ur[0])

    return zip(r.coords.xy[0], r.coords.xy[1])

