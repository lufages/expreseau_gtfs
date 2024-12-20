from setuptools import setup, find_packages

setup(
      name="expreseau_gtfs",
      version = "0.1",
      author="lucas fages",
      author_email="lucas.fages@cnrs.fr",
      url = "https://github.com/lufages/expreseau_gtfs/tree/main",
      packages=find_packages(),
      python_requires=">=3",
      install_requires = ['numpy', "pandas","geopandas","networkx",
                          "datetime", "shapely", "seaborn",
                          "matplotlib","tqdm", "scikit-learn", "requests",
                          "pyproj", "logging"], 
      
      # 
      
      classifiers=["Development Status :: 3 - Alpha",
                   "Environment :: Console",
                   "License :: Free For Educational Use"]
      
      
      )


