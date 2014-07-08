import numpy as np
import fiona
from shapely.geometry import Point, shape, asLineString, mapping
from shapely.ops import cascaded_union
import pandas as pd
import shutil
import GISio

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
    joined = shpdf.join(csvdf, on='node', how='inner', lsuffix='L', rsuffix='R')

    # write to shapefile
    GISio.df2shp(joined, out_shapefile, 'geometry', shapefile[:-4]+'.prj')

