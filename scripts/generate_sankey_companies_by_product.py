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
OUTPUT_DIR = '../sankeys'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# template for generating Sankey Diagram using Google charts
sankey_template = Template("""<!DOCTYPE html>
<html lang="en-US">
<body>

<h1>{{ title }} Sankey diagram</h1>

<div id="sankey"></div>

<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
       <div id="sankey_basic" style="width: 900px; height: 300px;"></div>

<script type="text/javascript">
google.charts.load('current', {'packages':['sankey']});
google.charts.setOnLoadCallback(drawChart);

function drawChart() {
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'From');
  data.addColumn('string', 'To');
  data.addColumn('number', 'Weight');
  data.addRows({{ edges }});

  // Sets chart options.
  var colors ={{ color_list }};


var options = {
height: 600,
//width: 800,
sankey: {
  node: {
    colors: colors
  },
  link: {
    colorMode: 'source',
    colors: colors
  },
  iterations: 1000,
}
};

  // Instantiates and draws our chart, passing in some options.
  var chart = new google.visualization.Sankey(document.getElementById('sankey'));
  chart.draw(data, options);
}

</script>

</body>
</html>""")

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  # load dataset into Pandas DataFrame
  #---------------------------------------------------------------------------#

  df = pd.read_csv( DATASET_FILE )

  # create output directory if it doesn't exist
  os.makedirs( OUTPUT_DIR )

  # list of hex colors for use in the Sankey diagram
  color_list = glasbey[:11]

  # 1. Create Sankey for most common company by product
  #---------------------------------------------------------------------------#

  products = list(np.array(Counter(df['Product']).most_common(10))[:, 0])
  edges = []

  for product in products:

    edges.append(['All', product, np.sum(df['Product'] == product) ])

    c = Counter(df[df['Product'] == product]['Company']).most_common(5)
    for company, count in c:
      edges.append([product, company, count])

  #---------------------------------------------------------------------------#

  output_file = os.path.join( OUTPUT_DIR, 'SANKEY-cfpb.html')
  edges_str = str( edges )
  edges_str = edges_str.replace('], [', '],\n[')
  with open( output_file, 'w' ) as f:
    f.write(sankey_template.render(
      edges = edges_str,
      color_list = color_list,
      title = 'CFPB'))

  # 2. Create Sankey for most common company by issue, for each product
  #---------------------------------------------------------------------------#

  for product in products:

    edges = [ ]

    issues = list(np.array(Counter(df[df['Product'] == product]['Issue']).most_common(10))[:, 0])

    for issue in issues:

      edges.append( [ product, issue, np.sum(((df['Product'] == product) & (df['Issue'] == issue)))] )
      c = Counter(df[((df['Product'] == product) & (df['Issue'] == issue))]['Company']).most_common(10)

      for company, count in c:
          edges.append([issue, company, count])

    edges_str = str( edges )
    edges_str =edges_str.replace('], [', '],\n[')

    product_name = product.replace(' ', '_')

    output_file = os.path.join(OUTPUT_DIR, f'SANKEY-{product_name}.html')
    with open(output_file, 'w') as f:
      f.write(sankey_template.render(
        edges = edges_str,
        color_list = color_list,
        title = product))

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#