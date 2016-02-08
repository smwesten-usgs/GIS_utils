import sys
sys.path.append('..')
import os
import numpy as np
import pandas as pd
from shapely.geometry import Point
from GISio import shp_properties
from GISio import df2shp, shp2df

def test_shp_properties():
    df = pd.DataFrame({'reach': [1], 'value': [1.0], 'name': ['stuff']}, index=[0])
    assert [d.name for d in df.dtypes] == ['object', 'int64', 'float64']
    assert shp_properties(df) == {'name': 'str', 'reach': 'int', 'value': 'float'}

def test_shp_read_and_write():

    # test without geometry
    df = pd.DataFrame({'reach': np.arange(10000001, 10000100, dtype=int), 'value': np.arange(1, 100, dtype=float),
                       'name': ['stuff{}'.format(i) for i in np.arange(1, 100)]})
    df2shp(df, 'temp/junk.dbf')
    df = shp2df('temp/junk.dbf')
    assert [d.name for d in df.dtypes] == ['object', 'int64', 'float64']

    # test with geometry
    df = pd.DataFrame({'reach': np.arange(1, 101, dtype=int), 'value': np.arange(100, dtype=float),
                       'name': ['stuff{}'.format(i) for i in np.arange(100)],
                       'geometry': [Point([i, i]) for i in range(100)]})
    original_columns = df.columns.tolist()
    df2shp(df, 'temp/junk.shp')
    df = shp2df('temp/junk.shp')
    assert df.geometry[0] == Point([0.0, 0.0])
    assert np.array_equal(df.index.values, np.arange(100)) # check ordering of rows
    assert df.columns.tolist() == original_columns # check column order

if __name__ == '__main__':
    if not os.path.isdir('temp'):
        os.makedirs('temp')
    test_shp_properties()
    test_shp_read_and_write()