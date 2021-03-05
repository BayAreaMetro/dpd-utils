# dpdutils

This package contains collection a of utilities to support the work of the Design and Project Delivery section at MTC. 

The type of utilities generally consist of downloading and working with traffic/transit data. Data sources include:
- Inrix
- Swiftly
- Bay Area Toll Authority
- Caltrans PeMS (modules not yet publicly available on this repo)

# Installation

Two methods are available for installing this package. This package is NOT distributed on a package repository like PyPI, so both methods below generally pip install directly from this repository.

## Method 1

To create a new conda environment that installs this package and all of it's dependencies, you can simply use the `environment.yml` included in this repository with the following terminal command:

`conda env create -f environment.yml`

## Method 2

If you already have an environment or just want to use pip, you can pip install this package directly from this GitHub repository using the following terminal command:

`pip install git+https://github.com/BayAreaMetro/dpdutils.git`

# Examples
Example scripts demonstrating how to use the modules in the package are provided in the [examples](./examples/) directory. 

# Contributors
- Elliot Huang (ehuang@bayareametro.gov)
