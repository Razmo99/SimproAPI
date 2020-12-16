# SimproAPI
Intended to be a Structured way to interface with Simpro's API.\
Its currently focused on the Plants & Equipment section of Simpro.

Has classes and methods for:
* Token Management - Get/Load/save/update
* Iterating over Plants & equipment to find trackable's

# Usage
Firstly you need to make up an instance of the TokenManager Class.\
This Class will be used to pass the retrieved Token to other methods later
~~~python
simpro_token=SimproAPI.TokenManager(
	server='https://XXXXXXXX.simprocloud.com'
	client_id='XXXXXXXXXXXXXXXXXXXXX'
	client_secret='XXXXXXXXXXXXXXXXXXXXX'
	username='XXXXXXXXXXXXXXXXXXXXX'
	password='XXXXXXXXXXXXXXXXXXXXX'
	save_location='simpro_token.json'
)
simpro_token.load_token() #Loads any token information in the save_location json file
simpro_token.update_token() # Check if the token is expired and renews if so.
~~~
Once the above is done we can actually pull some information from Simpro
~~~python
with SimproAPI.trackables(simpro_token.server,simpro_token.access_token) as trackables:
    trackables.get_companies(
        9000, #your_company_id
        [Serial,Location ] #list of custom_fields you are tracking
    )
~~~
The above Method is a big one. It will use sessions to iterate over the company and all plant types within.\
If the plant type has the custom fields specified it will then iterate over all plants and return the custom fields specified.

# Installation

`pip install SimproAPI`

