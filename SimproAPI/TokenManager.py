import requests
import json
from json import JSONEncoder
from .OAuth2 import OAuth2
import datetime
import logging

logger = logging.getLogger(__name__)
logger.debug('Importing Module : '+__name__)

#Class to handle saving datetime objects to JSON
class datetime_encoder(JSONEncoder):

    #Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()

class TokenManager(object):
    """Class to Manage Simpro Auth Token's"""
    def __init__(self,server,client_id,client_secret,username,password,save_location='simpro_token.json'):
        self.save_location=save_location
        self.access_token=''
        self.refresh_token=''
        self.refresh_token_expires=None
        self.expired=True
        self.expires=None
        self.client_id=client_id
        self.client_secret=client_secret
        self.username=username
        self.password=password
        self.server=server

    def get_token(self):
        """Get an authorisation token for future requests.
            Sets the results to the class object
        """
        logger.info("Token expired, initiating token renewal.")        
        #Use password grant type with username and password
        if not self.refresh_token:
            with OAuth2(self.server) as oauth2:
                token=oauth2.post(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    username=self.username,
                    password=self.password
                )
        #Otherwise use the refresh_token.
        else:
            with OAuth2(self.server) as oauth2:
                token=oauth2.post(
                client_id=self.client_id,
                client_secret=self.client_secret,
                refresh_token=self.refresh_token
                )
        #Create and set the expires date time
        time_now = datetime.datetime.now().astimezone()
        self.expires = time_now + datetime.timedelta(seconds=int(token['expires_in']))
        logger.info('Token Expires at: '+str(self.expires))
        self.expired = False
        #Set the header with the gathered data
        self.access_token = token['access_token']
        self.refresh_token=token['refresh_token']
        self.refresh_token_expires= time_now + datetime.timedelta(days=14)
        #Try to save the token to a file
        self.save_token()

    def save_token(self):
        """writes the token information to a file for later use
        """
        auth={
            'access_token':self.access_token,
            'expires':self.expires,
            'expired':self.expired,
            'refresh_token':self.refresh_token,
            'refresh_token_expires':self.refresh_token_expires
        }
        auth_json = json.dumps(auth,cls=datetime_encoder)        
        try:
            with open(self.save_location,'w') as auth_file:
                auth_file.write(auth_json)
            logger.info('Saved token to: '+ self.save_location)
        except PermissionError as e:
            logger.error(e)

    def load_token(self):
        """reads the token information from a file for later use
        """
        try:
            with open(self.save_location,'r') as saved_auth:
                cache_auth=saved_auth.read()
        except FileNotFoundError as e:
            logger.error(e)
        except PermissionError as e:
            logger.error(e)
        else:
            if cache_auth:
                #Convert the input to a dictionary
                auth_dict=json.loads(cache_auth)
                #Assign the values to class variables
                self.access_token=auth_dict['access_token']
                self.expires=datetime.datetime.fromisoformat(auth_dict['expires'])
                self.expired=auth_dict['expired']
                self.refresh_token=auth_dict['refresh_token']
                self.refresh_token_expires=datetime.datetime.fromisoformat(auth_dict['refresh_token_expires'])
                logger.info('Found '+self.save_location+' loading data')

    def update_token(self):
        """checks if the token is expired as requests another token if it is."""

        time_now = datetime.datetime.now().astimezone()
        time_now_plus_5=time_now + datetime.timedelta(minutes=5)
        result = False
        expires_valid = isinstance(self.expires,datetime.date)
        #If valid date and time_now is greater or equal than expired date
        if expires_valid and time_now_plus_5 >= self.expires and not self.expired:
                logger.debug('Auth token expires time >= time now')
                #Set the token to expired
                self.expired=True
                result = False
        #If the valid date and time_now is greater or equal than refresh token expires date
        elif expires_valid and time_now >= self.refresh_token_expires and not self.expired:
            logger.debug('Auth token expires time >= time now')
            #Set the token to expired
            self.expired=True
            result = False
        #If the token isnt expired read out the delta till expiration
        elif expires_valid and not self.expired:
                time_delta=(self.expires-time_now).seconds
                logger.info("Auth token not expired; Seconds left: "+str(time_delta))
                result = True
        #If the token is expired try to get another token
        if self.expired:
            logger.info("Auth token expired; Renewing")
            try:
                self.get_token()
            except SimproAPI.Exceptions.InvalidGrantRefreshTokenError:
                logger.warning('Invalid refresh token cleared.')
                self.refresh_token=''
                self.get_token()
            except:
                logger.exception('')
            else:
                result = True
        return result