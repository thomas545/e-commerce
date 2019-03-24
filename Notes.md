

- for dump data from database:

python manage.py dumpdata products --format json --indent 4 > products/fixures/products.json


- For loading data into database:

python manage.py loaddata products/fixures/products.json
