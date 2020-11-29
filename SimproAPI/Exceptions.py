class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class SimproErrorHandler(object):
    """Handles Simpro Exceptions"""

    def __init__(self,request):
        self.status_code=request.status_code
        if self.status_code == 401:
            raise SessionsUnauthorize()
        elif self.status_code == 404:
            raise SessionsPlantOrEquipmentNotFoundError()
        elif self.status_code == 422:
            raise SessionsPlantOrEquipmentNotFoundError()
        
            
class SessionsUnauthorize(Error):
    """Exception raised when 401 is returned fom requests"""
class SessionsGetPlantOrEquipmentNotFoundError(Error):
    """Exception raised when 404 is returned fom requests"""
class SessionsPatchInvalidDataError(Error):
    """Exception raised when 422 is returned fom requests"""

class InvalidCredentialError(Error):
    """Exception raised for errors related to Invalid Credentials."""

    def __init__(self, message='Invalid username and password combination'):
        self.message = message

class InvalidGrantTypeError(Error):
    """Exception raised for errors related to Invalid Grant Type."""

class InvalidGrantRefreshTokenError(Error):
    """Exception raised for errors related to Invalid Grant Refresh Token."""
class UndefinedFaultStringError(Error):
    """Exception raised for unhandled errors."""

    def __init__(self,expression, message):
        self.message = message
        self.expression = expression