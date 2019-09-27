# -*- coding: UTF-8 -*-

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os
from collections import Counter

import pandas as pd
import numpy as np

from jinja2 import Template

from colorcet import glasbey

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# CFPB data downloaded from
# https://www.consumerfinance.gov/data-research/consumer-complaints/search/?from=0&searchField=all&searchText=&size=25&sort=created_date_desc
DATASET_FILE = '../Consumer_Complaints.csv'

# directory to output bar charts to
OUTPUT_DIR = '../dashboards'

# number of companies to include per category
N_COMPANIES = 10

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# template for generating Sankey Diagram using Google charts
sankey_template = Template("""<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>

<title>
          Google Visualization API Sample
        </title>

<script type="text/javascript" src="http://www.google.com/jsapi"></script>
<script type="text/javascript">
  google.load('visualization', '1.1', {packages: ['controls']});
</script>
<script type="text/javascript">

function drawVisualization() {

// Prepare the data
      var data1 = google.visualization.arrayToDataTable({{data}});

  // Define a category picker control for the Type column



 var categoryPicker = new google.visualization.ControlWrapper({
    'controlType': 'CategoryFilter',
    'containerId': 'control',
    'options': {
      'filterColumnLabel': 'Product',
      'ui': {
      'labelStacking': 'vertical',
        'allowTyping': false,
        'allowMultiple': false,
      }
    },
    'state': {
        'selectedValues': ['All']
    }
  });

  // Define a table

 var columns_kpi = new google.visualization.ChartWrapper({
    'chartType': 'BarChart',
    'containerId': 'chart',
    'options': {
      'height': 600,
      'title': 'CFPB Complaints by Company and Category',
      'chartArea': {left:'45%',top:'10&',width:'50%',height:'50%'},
      'hAxis': {
       'title': 'Number of Complaints',
        'maxTextLines': 1,
        },
        'legend': {position: 'none'}
      //'pieSliceText': 'label'
    },

    // Instruct the piechart to use columns 0 (company) and 2 (number of complaints)
    // from the 'data' DataTable.
    'view': {'columns': [0, 2]}
  });


  // Create a dashboard
  new google.visualization.Dashboard(document.getElementById('dashboard_alarms'));
  new google.visualization.Dashboard(document.getElementById('dashboard_kpi')).
      // Establish bindings, declaring the both the slider and the category
      // picker will drive both charts.
      bind([categoryPicker], [columns_kpi,]).
      // Draw the entire dashboard.
      draw(data1);

}


      google.setOnLoadCallback(drawVisualization);
    </script>
  </head>
  <body style="font-family: Arial;border: 0 none;">
    <div id="dashboard">
      <table>
        <tr style='vertical-align: top'>
          <td style='width: 200px; font-size: 0.9em;'>
            <div id="control"></div>
          </td>
          <td style='height: 600px'>
            <div style="float: left;" id="chart"></div>
          </td>
        </tr>
      </table>
    <div id="dashboard_alarms"/>
    <div id="dashboard_kpi"/>
    </div>
  </body>
</html>

""")

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  # load dataset into Pandas DataFrame
  #---------------------------------------------------------------------------#

  df = pd.read_csv( DATASET_FILE )

  # create output directory if it doesn't exist
  os.makedirs( OUTPUT_DIR, exist_ok = True )

  # 1. Create Sankey for most common company by product
  #---------------------------------------------------------------------------#

  products = sorted(list(set(df['Product'])))[:-1]

  # initialize dict containing company names and complaint counts, for each
  # product
  product_bar_dict = dict()

  # get most complained about companies, across ALL products
  #---------------------------------------------------------------------------#

  # use Counter to get the most common companies and complaint counts for all
  # products
  cmc = np.asarray(
    Counter(
      df['Company']).most_common(N_COMPANIES))

  # extract company names
  company_names = cmc[:, 0]

  # extract complaint counts
  company_counts = np.asarray(cmc[:, 1], dtype = np.int)

   # save tuple of company names and complaint counts as the value of the
  # dict, for the key `All`
  product_bar_dict['All'] = (company_names, company_counts)

  # get most complained-about companies by product
  #---------------------------------------------------------------------------#

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

  # convert dict to 2D list
  #---------------------------------------------------------------------------#

  data = []
  data.append(['Company', 'Product', 'Complaints'])
  for i in range(N_COMPANIES):
    for product in product_bar_dict.keys( ):
      tpl = product_bar_dict[product]
      company = tpl[0][i]
      count = tpl[1][i]
      entry = [company, product, count ]
      data.append(entry)

  data_str = str( data )
  data_str =data_str.replace('], [', '],\n[')

  product_name = product.replace(' ', '_')

  # fill html template, write to file
  #---------------------------------------------------------------------------#

  output_file = os.path.join(OUTPUT_DIR, f'BAR-dashboard.html')
  with open(output_file, 'w') as f:
    f.write(sankey_template.render(
      data = data_str))

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#