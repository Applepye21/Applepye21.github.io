rm -r ../docs/*
cp ../index.md ../home.md
python3 python_scripts/add_toctree.py
sphinx-build .. ../docs
python3 python_scripts/delete_toctree.py
touch ../docs/.nojekyll
rm -r  jupyter_execute
rm ../home.md
