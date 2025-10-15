rm -r ../docs/*
mv ../README.md ../README.txt
python python_scripts/add_toctree.py
sphinx-build .. ../docs
python python_scripts/delete_toctree.py
mv ../README.txt ../README.md
touch ../docs/.nojekyll
python python_scripts/change_vortex_links.py
rm ../docs/.doctrees/environment.pickle

