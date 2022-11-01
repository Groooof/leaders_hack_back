import typing as tp
import pydantic as pd


class CustomHTTPException(Exception):
    def __init__ (self,
                  status_code: int,
                  error: tp.Optional[str] = None,
                  error_description: tp.Optional[str] = None,
                  headers: tp.Optional[dict] = None,
                  ) -> None:
        self.status_code = status_code
        self.error = error
        self.error_description = error_description
        self.headers = headers
        
    def __call__(self, 
                 status_code: tp.Optional[int] = None,
                 error: tp.Optional[str] = None,
                 error_description: tp.Optional[str] = None,
                 headers: tp.Optional[dict] = None,) -> 'CustomHTTPException':
        self.status_code = status_code if status_code is not None else self.status_code
        self.error = error if error is not None else self.error
        self.error_description = error_description if error_description is not None else self.error_description
        self.headers = headers if headers is not None else self.headers
        return self
        
                
    # @property
    # def schema(self):
    #     return {
    #         self.status_code: {
    #         "description": self.error_description,
    #         "content": {
    #             "application/json": {
    #                 "example":  {'error': self.error, 
    #                              'error_description' : self.error_description}
    #                 }
    #             }
    #         }
    #         }
        
            
    
    
# class CustomHTTPException(pd.BaseModel, Exception):
#     status_code: int
#     error: tp.Optional[str]
#     error_description: tp.Optional[str]
#     headers: tp.Optional[dict]
    
    
# class InvalidRequestException(CustomHTTPException):
#     status_code: int = 400
#     error: tp.Optional[str] = 'invalid_request_!'
    
    
INVALID_REQUEST_EXCEPTION = CustomHTTPException(400, 'invalid_request', 'Invalid request data')
    
# class InvalidRequestException(CustomHTTPException):
#     def __init__(self, description: tp.Optional[str] = None, headers: tp.Optional[dict] = None) -> None:
#         super().__init__(400, 'invalid_request', description, headers)



    
