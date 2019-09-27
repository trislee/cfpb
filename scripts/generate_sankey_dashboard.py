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
  google.load('visualization', '1.1', {packages: ['controls', 'sankey']});
</script>
<script type="text/javascript">

function drawVisualization() {

// Prepare the data
      var data1 = google.visualization.arrayToDataTable({{ edges }});

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

 var colors = {{ color_list }};
  // Define a table

 var columns_sankey = new google.visualization.ChartWrapper({
    'chartType': 'Sankey',
    'containerId': 'chart',
    'options': {
      'height': 600,
      'title': 'CFPB Complaints by Company and Category',
      sankey: {
        node: {
          colors: colors
        },
        link: {
          colorMode: 'source',
          colors: colors
        },
        iterations : 1000
      }
      //'pieSliceText': 'label'
    },

    // Instruct the piechart to use colums 0 (Name) and 3 (Donuts Eaten)
    // from the 'data' DataTable.
    'view': {'columns': [0,1,2]}
  });


  // Create a dashboard
  new google.visualization.Dashboard(document.getElementById('dashboard_sankey')).
      // Establish bindings, declaring the both the slider and the category
      // picker will drive both charts.
      bind([categoryPicker], [columns_sankey]).
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
          <td style='height: 800px'>
            <div style="float: left;" id="chart"></div>
          </td>
        </tr>
      </table>
    <div id="dashboard_sankey"/>
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

  # list of hex colors for use in the Sankey diagram
  color_list = glasbey[:51]

  # 1. Create Sankey for most common company by product
  #---------------------------------------------------------------------------#

  products = list(np.array(Counter(df['Product']).most_common(10))[:, 0])
  edges = []
  edges.append(['Source', 'Target', 'Count', 'Product'])

  for product in products:

    edges.append(['All', product, np.sum(df['Product'] == product), 'All' ])

    c = Counter(df[df['Product'] == product]['Company']).most_common( 5 )
    for company, count in c:
      edges.append([product, company, count, 'All'])

  # 2. Create Sankey for most common company by issue, for each product
  #---------------------------------------------------------------------------#

  for product in products:

    issues = list(np.array(Counter(df[df['Product'] == product]['Issue']).most_common(10))[:, 0])

    for issue in issues:

      edges.append( [product, issue, np.sum(((df['Product'] == product) & (df['Issue'] == issue))), product] )
      c = Counter(df[((df['Product'] == product) & (df['Issue'] == issue))]['Company']).most_common(5)

      for company, count in c:
          edges.append([issue, company, count, product])

  edges_str = str( edges )
  edges_str =edges_str.replace('], [', '],\n[')

  product_name = product.replace(' ', '_')

  output_file = os.path.join(OUTPUT_DIR, f'SANKEY-dashboard.html')
  with open(output_file, 'w') as f:
    f.write(sankey_template.render(
      edges = edges_str,
      color_list = color_list))

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#