# -*- coding: UTF-8 -*-

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

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
OUTPUT_DIR= '../companies_by_product'

# number of companies to plot
N_COMPANIES = 10

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  # load dataset into Pandas DataFrame
  #---------------------------------------------------------------------------#

  df = pd.read_csv( DATASET_FILE )

  # create dict of most complained-about companies for each product category
  #---------------------------------------------------------------------------#

  # create list of all product categories (skipping the last one because it's
  # very small)
  products = sorted(list(set(df['Product'])))[:-1]

  # initialize dict containing company names and complaint counts, for each
  # product
  product_bar_dict = dict()

  # loop over products
  for product in products:

    # use Counter to get the most common companies and complaint counts for a
    # given product
    cmc = np.asarray(
      Counter(
        df[df['Product'] == product]['Company']).most_common(N_COMPANIES))

    # extract company names
    company_names = cmc[:, 0]

    # extract complaint counts
    company_counts = np.asarray(cmc[:, 1], dtype = np.int)

    # save tuple of company names and complaint counts as the value of the
    # dict, for the key `product`
    product_bar_dict[product] = (company_names, company_counts)

  # for each category generate and save a bar chart of the most complained-about
  # companies
  #---------------------------------------------------------------------------#

  os.makedirs( OUTPUT_DIR, exist_ok = True )

  for product in products:

    # get company names and complaint counts for a given product
    company_names, company_counts = product_bar_dict[product]

    # reverse the arrays so the largest bars are at the top
    company_names = company_names[::-1]
    company_counts = company_counts[::-1]

    y_arr = np.arange(1, 11)
    fig, ax = plt.subplots(figsize = (8, 6))
    ax.barh(y_arr, company_counts)

    ax.set_yticks(y_arr)
    ax.set_yticklabels(company_names)
    ax.set_ylim(0, 11)

    fig.suptitle( product, y=0.975, fontsize = 16, fontweight='bold' )

    # set max number of x ticks, so numbers don't get too cluttered
    plt.locator_params(axis = 'x', nbins=6)

    # only have gridlines in the x axis dimension
    ax.yaxis.grid(False)

    ax.set_xlabel('Number of complaints')

    plt.tight_layout()
    plt.subplots_adjust(top=0.925)

    # pad the left of the plot so the company's full name is shown
    plt.gcf().subplots_adjust(left=0.55)

    product_name = product.replace(' ', '_')
    plt.savefig(os.path.join(OUTPUT_DIR, f'{product_name}.svg'))
    plt.close()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#