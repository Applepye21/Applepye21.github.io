import os

#Extract lines from the HTML file
html_file = open('../docs/projects.html', 'r', encoding='utf-8')
html_lines = [line for line in html_file]
html_file.close()

os.remove('../docs/projects.html')

bad_link_list = [
    'https://vortex.plymouth.edu/mapwall/sfc/global/loop.html?region_name=us&amp;amp;prod_name=cloud',
    'https://vortex.plymouth.edu/mapwall/sfc/global/loop.html?region_name=us&amp;amp;prod_name=dew_point_temperature',
    'https://vortex.plymouth.edu/mapwall/sfc/global/loop.html?region_name=us&amp;amp;prod_name=heat_index',
    'https://vortex.plymouth.edu/mapwall/sfc/global/loop.html?region_name=us&amp;amp;prod_name=wind_chill_temperature'
]
good_link_list = [
    'https://vortex.plymouth.edu/mapwall/sfc/global/loop.html?region_name=us&prod_name=cloud',
    'https://vortex.plymouth.edu/mapwall/sfc/global/loop.html?region_name=us&prod_name=dew_point_temperature',
    'https://vortex.plymouth.edu/mapwall/sfc/global/loop.html?region_name=us&prod_name=heat_index',
    'https://vortex.plymouth.edu/mapwall/sfc/global/loop.html?region_name=us&prod_name=wind_chill_temperature'
]

new_html = open('../docs/projects.html', 'w', encoding='utf-8')
for line in html_lines:
    for i in range(len(bad_link_list)):
        line = line.replace(bad_link_list[i], good_link_list[i])
    new_html.write(line)
new_html.close()
