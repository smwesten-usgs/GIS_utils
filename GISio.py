import numpy as np
import fiona
from shapely.geometry import Point, shape, asLineString, mapping
import pandas as pd
import shutil

def shp2df(shp, geometry=False):
    '''
    Read shapefile into Pandas dataframe
    shp = shapefile name
    '''
    print "loading attributes from {} into pandas dataframe...".format(shp)
    shp_obj = fiona.open(shp, 'r')

    attributes_dict = {}
    knt = 0
    length = len(shp_obj)
    for line in shp_obj:
        props = line['properties']
        if geometry:
            geometry = shape(line['geometry'])
            props['geometry'] = geometry
        attributes_dict[line['id']] = props
        knt += 1
        print '\r{:d}%'.format(100*knt/length),
    print '\n'
    # convert to pandas dataframe, join in centroids, sort by FID
    shp_df = pd.DataFrame.from_dict(attributes_dict, orient='index')

    return shp_df


def shp_properties(df):
    # convert dtypes in dataframe to 32 bit
    i = -1
    dtypes = list(df.dtypes)
    for dtype in dtypes:
        i += 1
        if dtype == np.dtype('float64'):
            continue
            #df[df.columns[i]] = df[df.columns[i]].astype('float32')
        elif dtype == np.dtype('int64'):
            df[df.columns[i]] = df[df.columns[i]].astype('int32')
    # strip dtypes just down to 'float' or 'int'
    dtypes = [''.join([c for c in d.name if not c.isdigit()]) for d in list(df.dtypes)]
    # also exchange any 'object' dtype for 'str'
    dtypes = [d.replace('object', 'str') for d in dtypes]
    properties = dict(zip(df.columns, dtypes))
    return properties


def shpfromdf(df, shpname, Xname, Yname, prj):
    '''
    creates point shape file from pandas dataframe
    shp: name of shapefile to write
    Xname: name of column containing Xcoordinates
    Yname: name of column containing Ycoordinates
    '''
    '''
    # convert dtypes in dataframe to 32 bit
    i = -1
    dtypes = list(df.dtypes)
    for dtype in dtypes:
        i += 1
        if dtype == np.dtype('float64'):
            continue
            #df[df.columns[i]] = df[df.columns[i]].astype('float32')
        elif dtype == np.dtype('int64'):
            df[df.columns[i]] = df[df.columns[i]].astype('int32')
    # strip dtypes just down to 'float' or 'int'
    dtypes = [''.join([c for c in d.name if not c.isdigit()]) for d in list(df.dtypes)]
    # also exchange any 'object' dtype for 'str'
    dtypes = [d.replace('object', 'str') for d in dtypes]

    properties = dict(zip(df.columns, dtypes))
    '''
    properties = shp_properties(df)
    schema = {'geometry': 'Point', 'properties': properties}

    with fiona.collection(shpname, "w", "ESRI Shapefile", schema) as output:
        for i in df.index:
            X = df.iloc[i][Xname]
            Y = df.iloc[i][Yname]
            point = Point(X, Y)
            props = dict(zip(df.columns, df.iloc[i]))
            output.write({'properties': props,
                          'geometry': mapping(point)})
    shutil.copyfile(prj, "{}.prj".format(shpname[:-4]))


def df2shp(df, shpname, geo_column, prj):
    '''
    like above, but requires a column of shapely geometry information
    '''
    print 'writing {}...'.format(shpname)
    properties = shp_properties(df)
    del properties[geo_column]

    Type = df.iloc[1]['geometry'].type
    schema = {'geometry': Type, 'properties': properties}
    length = len(df)
    knt = 0
    with fiona.collection(shpname, "w", "ESRI Shapefile", schema) as output:
        for i in range(len(df)):
            geo = df.iloc[i][geo_column]
            props = dict(zip(df.columns, df.iloc[i]))
            del props[geo_column]
            output.write({'properties': props,
                          'geometry': mapping(geo)})
            knt +=1
            print '\r{:d}%'.format(100*knt/length),
    shutil.copyfile(prj, "{}.prj".format(shpname[:-4]))


def linestring_shpfromdf(df, shpname, IDname, Xname, Yname, Zname, prj, aggregate=None):
    '''
    creates point shape file from pandas dataframe
    shp: name of shapefile to write
    Xname: name of column containing Xcoordinates
    Yname: name of column containing Ycoordinates
    Zname: name of column containing Zcoordinates
    IDname: column with unique integers for each line
    aggregate = dict of column names (keys) and operations (entries)
    '''

    # setup properties for schema
    # if including other properties besides line identifier,
    # aggregate those to single value for line, using supplied aggregate dictionary
    if aggregate:
        cols = [IDname] + aggregate.keys()
        aggregated = df[cols].groupby(IDname).agg(aggregate)
        aggregated[IDname] = aggregated.index
        properties = shp_properties(aggregated)
    # otherwise setup properties to just include line identifier
    else:
        properties = {IDname: 'int'}
        aggregated = pd.DataFrame(df[IDname].astype('int32'))

    schema = {'geometry': '3D LineString', 'properties': properties}
    lines = list(np.unique(df[IDname].astype('int32')))

    with fiona.collection(shpname, "w", "ESRI Shapefile", schema) as output:
        for line in lines:

            lineinfo = df[df[IDname] == line]
            vertices = lineinfo[[Xname, Yname, Zname]].values
            linestring = asLineString(vertices)
            props = dict(zip(aggregated.columns, aggregated.ix[line, :]))
            output.write({'properties': props,
                          'geometry': mapping(linestring)})
    shutil.copyfile(prj, "{}.prj".format(shpname[:-4]))