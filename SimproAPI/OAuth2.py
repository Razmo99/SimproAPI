import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .Exceptions import (InvalidCredentialError, InvalidGrantRefreshTokenError,InvalidGrantTypeError, UndefinedFaultStringError)

logger = logging.getLogger(__name__)
logger.debug('Importing Module : '+__name__)

class OAuth2(object):
    """Class to manage Simpro API Sessions"""
    def __init__(self,server):
        self.server=server
        self.session=requests.Session()
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

    def post(self,client_id,client_secret,username=None,password=None,refresh_token=None):
        """post an authorization token
            Arguments:
            Returns:
                dictionary -- Returns OAuth2 Information:
                    {
                        "access_token": "XXXXXXXXXXXXXXXXXXXXX",
                        "expires_in": 3600,
                        "token_type": "Bearer",
                        "scope": null,
                        "refresh_token": "XXXXXXXXXXXXXXXXXXXXX"
                    }
        """
        data={
            "grant_type":"",
            "client_id": client_id,
            "client_secret": client_secret
        }        
        if username and password and not refresh_token:
            logger.debug('Posting OAuth2 with grant_type=password')
            data['username']=username
            data['password']=password
            data['grant_type']='password'
        elif refresh_token:
            logger.debug('Posting OAuth2 with grant_type=refresh_token')
            data['refresh_token']=refresh_token
            data['grant_type']='refresh_token'
        else:
            raise Exception('A username & password or refresh token must be specified')

        uri = '/oauth2/token'
        url = self.server + uri
        results = self.session.post(
            url,
            data=data,
            timeout=5).json()
        if results.get('error'):
            if results.get('error_description') == 'Invalid username and password combination':
                raise CredentialError()
            elif results.get('error_description') == 'The grant type was not specified in the request':
                raise InvalidGrantTypeError()
            elif results.get('error_description') == 'Invalid refresh token':
                raise InvalidGrantRefreshTokenError()
            else:
                UndefinedFaultStringError(results,results['error_description'])
        else:   
            return results
        
