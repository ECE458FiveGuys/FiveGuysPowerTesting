# Instructions

run `python manage.py runserver`

Make GET request to <http://127.0.0.1:8000/auth/token/login/>

Save the TOKEN received

For subsequent queries, we will need token to be sent with the request. To do this, we must have the token in the 
headers by using the key `Authorization` and value `Token ######`, which is to say the word "Token" + SPACE + Token Value

To received list of models, make GET request to <http://127.0.0.1:8000/models>

To make a model, make POST request to <http://127.0.0.1:8000/models> with body form-data with at least the keys `vendor`
, `model_number` and `description`.

To make an instrument, make POST request to <http://127.0.0.1:8000/instruments> with body form-data with at least the
keys `model` (where here `model` is the PK of an existing model) and `serial_number`.

Queries can be made to endpoints for models and instruments how one would usually do queries. For example, if I wanted
to make a query to get all instruments from vendor `VENDOR_NAME`, I would make a POST request with the following query parameters:
<http://127.0.0.1:8000/instruments?vendor=VENDOR_NAME>. If I wanted the instrument with `serial_number = 69` from the same
vendor, the POST request would be written instead like <http://127.0.0.1:8000/instruments?vendor=VENDOR_NAME&serial_number=69>

For questions about which fields can be queried from models and instruments, please refer to the sprint 1 requirements.