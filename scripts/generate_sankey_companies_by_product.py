# -*- coding: UTF-8 -*-

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os
from collections import Counter

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
plt.style.use( 'trislee' )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# CFPB data downloaded from
# https://www.consumerfinance.gov/data-research/consumer-complaints/search/?from=0&searchField=all&searchText=&size=25&sort=created_date_desc
DATASET_FILE = '../Consumer_Complaints.csv'

# directory to output bar charts to
OUTPUT_FILE= '../sankeys/cfpb_edges.txt'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  # load dataset into Pandas DataFrame
  #---------------------------------------------------------------------------#

  df = pd.read_csv( DATASET_FILE )

  # create dict of most complained-about companies for each product category
  #---------------------------------------------------------------------------#

  products = list(np.array(Counter(df['Product']).most_common(10))[:, 0])
  edges = []

  for product in products:

    edges.append(['All', product, np.sum(df['Product'] == product) ])

    c = Counter(df[df['Product'] == product]['Company']).most_common(5)
    for company, count in c:
      edges.append([product, company, count])

  #---------------------------------------------------------------------------#

  edges_str = str( edges )
  edges_str =edges_str.replace('], [', '],\n[')
  with open( OUTPUT_FILE, 'w' ) as f:
    f.write(edges_str)

  #---------------------------------------------------------------------------#

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#