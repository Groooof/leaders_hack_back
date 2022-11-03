from src.utils.custom import CustomHTTPException


WRONG_FILES_FORMAT = CustomHTTPException(415, 'wrong_files_format')
FILE_NOT_FOUND = CustomHTTPException(404, 'not_found')
