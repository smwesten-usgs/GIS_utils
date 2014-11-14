from distutils.core import setup

DESCRIPTION = """\
Convenience functions for transferring information between shapefiles, 
pandas dataframes, and csv or Excel files. Also for GIS operations
in pandas (in development).
"""

def run():
    setup(name="GIS_utils",
          version="0.1",
          description="GIS with pandas",
          author="Andy Leaf",
          packages=[""],
          long_descripton=DESCRIPTION,
          )
          
if __name__ == "__main__":
    run()