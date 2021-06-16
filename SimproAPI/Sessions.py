import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .Exceptions import SimproErrorHandler

logger = logging.getLogger(__name__)
logger.debug('Importing Module : '+__name__)

class Sessions(object):
    """Class to manage Simpro API Sessions"""
    def __init__(self,server,token):
        self.server=server
        self.token=token
        self.session=requests.Session()
        self.headers={'Authorization': 'Bearer {0}'.format(token),'Accept':'application/json'}
        self.session.headers.update(self.headers)
        self.session.mount(
            'https://',
            HTTPAdapter(
                max_retries=Retry(
                    total=5,
                    backoff_factor=0.5)))

    def __enter__(self):
        return self
    
    def __exit__(self,exec_types,exec_val,exc_tb):
        self.session.close()

    def companies_get_all(self,params={}):
        """Gets a list of all companies in the client's build.
            
            Arguments:
                params {dict} -- Params/query options to pass to the request
            Returns:
                requests object
        """

        uri = '/api/v1.0/companies/'      
        url = self.server + uri
        results = self.session.get(
            url,            
            params=params,
            timeout=5)
        if results.ok:
            return results
        else:
            SimproErrorHandler(results)

    def companies_get_specific(self,company_id,params={}):
        """Get list of Companies from the client's build
            
            Arguments:
                company_id {int} -- ID of the company
                params {dict} -- Params/query options to pass to the request
            Returns:
                requests object
        """
        uri = '/api/v1.0/companies/{0}'.format(company_id)         
        url = self.server + uri
        results = requests.get(
            url,
            timeout=5,
            params=params
            )
        if results.ok:
            return results
        else:
            SimproErrorHandler(results)

    def plants_and_equipment_get_all(self,company_id,plant_type_id,params={}):
        """Get all plant and equipment

            Notes:
                Can Handle Pagination
            
            Arguments:
                company_id {integer} -- ID of the company
                plant_type_id {integer} -- ID of the plant type
                params {dict} -- Params/query options to pass to the request
            Yields:
                requests object
        """
        current_page=1
        last_page=1
        uri = '/api/v1.0/companies/{0}/plantTypes/{1}/plants/'.format(company_id,plant_type_id)
        url = self.server + uri
        params['page']=current_page
        while(current_page <= last_page):
            page=self.session.get(
                url,
                params=params,
                timeout=5
                )
            if page.headers.get('Result-Pages'):
                last_page=int(page.headers.get('Result-Pages'))
            current_page += 1
            params['page']=current_page
            yield page

    def plants_and_equipment_get_specific(self,company_id,plant_type_id,plant_id,params={}):
            """Get details from a specific plant and equipment
                
                Arguments:
                    company_id {integer} -- ID of the company
                    plant_type_id {integer} -- ID of the plant type
                params {dict} -- Params/query options to pass to the request
                Returns:
                    requests object
            """

            uri = '/api/v1.0/companies/{0}/plantTypes/{1}/plants/{2}'.format(company_id,plant_type_id,plant_id)
            url = self.server + uri
            results = self.session.get(
                url,
                timeout=5,
                params=params
                )
            if results.ok:
                return results
            else:
                SimproErrorHandler(results)       

    def plants_and_equipment_custom_fields_get_all(self,company_id,plant_type_id,plant_id,params={}):
        """Get all plant and equipment Custom Fields
        
            Arguments:
                company_id {integer} -- ID of the company
                plant_type_id {integer} -- ID of the plant type
                plant_id {interger} -- ID of the plant            
                params {dict} -- Params/query options to pass to the request
            Returns:
                requests object
        """

        uri = '/api/v1.0/companies/{0}/plantTypes/{1}/plants/{2}/customFields/'.format(company_id,plant_type_id,plant_id)     
        url = self.server + uri
        results = self.session.get(
            url,
            timeout=5,
            params=params)
        if results.ok:
            return results
        else:
            SimproErrorHandler(results)

    def plants_and_equipment_custom_fields_get_specific(self,company_id,plant_type_id,plant_id,custom_field_id,params={}):
        """Get details from a specific plant and equipment Custom Field
            
            Arguments:
                server {string} -- Server URI
                token {string} -- Token value to be used for accessing the API
                company_id {integer} -- ID of the company
                plant_type_id {integer} -- ID of the plant type
                plant_id {interger} -- ID of the plant
                custom_field_id {interger} -- ID of the Custom Field
                params {dict} -- Params/query options to pass to the request
            Returns:
                requests object
        """

        uri = '/api/v1.0/companies/{0}/plantTypes/{1}/plants/{2}/customFields/{3}'.format(company_id,plant_type_id,plant_id,custom_field_id)
        url = self.server + uri
        results = self.session.get(
            url,
            timeout=5,
            params=params)
        if results.ok:
            return results
        else:
            SimproErrorHandler(results)

    def plants_and_equipment_custom_fields_patch_specific(self,company_id,plant_type_id,plant_id,custom_field_id,data):
        """Patch details to a specific plant and equipment Custom Field
        
            Arguments:
                company_id {integer} -- ID of the company
                plant_type_id {integer} -- ID of the plant type
                plant_id {interger} -- ID of the plant
                custom_field_id {interger} -- ID of the Custom Field
                params {dict} -- Params/query options to pass to the request
            Returns:
                requests object
        """

        uri = '/api/v1.0/companies/{0}/plantTypes/{1}/plants/{2}/customFields/{3}'.format(company_id,plant_type_id,plant_id,custom_field_id)
        url = self.server + uri
        results = self.session.patch(
            url,
            data=data,
            timeout=5
            )
        if results.ok:
            return results
        else:
            SimproErrorHandler(results)

    def plant_type_get_all(self,company_id,params={}):
        """Get all Plant Types from a company
            
            Arguments:
                company_id {integer} -- ID of the company
                params {dict} -- Params/query options to pass to the request
            Returns:
                requests object
        """

        uri = "/api/v1.0/companies/{0}/plantTypes/".format(company_id)      
        url = self.server + uri
        results = self.session.get(
            url,
            params=params,
            timeout=5
            )
        if results.ok:
            return results
        else:
            SimproErrorHandler(results)

    def plant_type_custom_fields_get_all(self,company_id,plant_type_id,params={}):
        """Get all plant and equipment Custom Fields
            
            Arguments:
                company_id {integer} -- ID of the company
                plant_type_id {integer} -- ID of the plant type
                plant_id {interger} -- ID of the plant            
                params {dict} -- Params/query options to pass to the request
            Returns:
                requests object
        """

        uri = '/api/v1.0/companies/{0}/plantTypes/{1}/customFields/'.format(company_id,plant_type_id) 
        url = self.server + uri
        results = self.session.get(
            url,
            params=params,
            timeout=1)
        if results.ok:
            return results
        else:
            SimproErrorHandler(results)

    def plant_type_custom_fields_get_specific(self,company_id,plant_type_id,plant_id,plant_type_custom_field_id,params={}):
        """Get details from a specific plant and equipment Custom Field
            
            Arguments:
                company_id {integer} -- ID of the company
                plant_type_id {integer} -- ID of the plant type            
                plant_type_custom_field_id {interger} -- ID of the Custom Field
                params {dict} -- Params/query options to pass to the request
            Returns:
                requests object
        """

        uri = '/api/v1.0/companies/{0}/plantTypes/{1}/plants/customFields/{3}'.format(company_id,plant_type_id,plant_id,plant_type_custom_field_id)
        url = self.server + uri
        results = self.session.get(
            url,            
            params=params,
            timeout=5
            )            
        if results.ok:
            return results
        else:
            SimproErrorHandler(results)
