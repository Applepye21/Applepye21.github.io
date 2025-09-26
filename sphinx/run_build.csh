rm -r ../docs/*
mv ../README.md ../README.txt
sphinx-build .. ../docs
mv ../README.txt ../README.md
touch ../docs/.nojekyll

