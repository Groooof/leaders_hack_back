import os
import shutil
from zipfile import (
    ZipFile,
    ZipInfo
)


class CustomZipFile(ZipFile):
    def extract(self, member, path=None, pwd=None, parents=True, filename=None):
        if path is None:
            path = os.getcwd()
        else:
            path = os.fspath(path)

        return self._extract_member(member, path, pwd, parents=parents, filename=filename)
    
    def _extract_member(self, member, targetpath, pwd, parents, filename):
        """Extract the ZipInfo object 'member' to a physical
           file on the path targetpath.
        """
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        # build the destination pathname, replacing
        # forward slashes to platform specific separators.
        arcname = member.filename.replace('/', os.path.sep)



        if os.path.altsep:
            arcname = arcname.replace(os.path.altsep, os.path.sep)
        # interpret absolute pathname as relative, remove drive letter or
        # UNC path, redundant separators, "." and ".." components.
        arcname = os.path.splitdrive(arcname)[1]
        

        
        invalid_path_parts = ('', os.path.curdir, os.path.pardir)
        arcname = os.path.sep.join(x for x in arcname.split(os.path.sep)
                                   if x not in invalid_path_parts)
        
        if os.path.sep == '\\':
            # filter illegal characters on Windows
            arcname = self._sanitize_windows_name(arcname, os.path.sep)

        # custom
        filename = arcname.split('/')[-1] if filename is None else filename
        if not parents:
            arcname = filename

        targetpath = os.path.join(targetpath, arcname)
        targetpath = os.path.normpath(targetpath)


        # Create all upper directories if necessary.
        upperdirs = os.path.dirname(targetpath)
        if upperdirs and not os.path.exists(upperdirs):
            os.makedirs(upperdirs)

        if member.is_dir():
            if not os.path.isdir(targetpath):
                os.mkdir(targetpath)
            return targetpath

        with self.open(member, pwd=pwd) as source, \
             open(targetpath, "wb") as target:
            shutil.copyfileobj(source, target)

        return targetpath


class ExtensionsValidators:
    _dicom = {'.dcm'}
    _archive = {'.zip'}
    _json = {'.json'}

    @classmethod
    def is_json(cls, filename: str) -> bool:
        return cls._get_extension(filename) in cls._json

    @classmethod
    def is_dicom(cls, filename: str) -> bool:
        return cls._get_extension(filename) in cls._dicom
    
    @classmethod
    def is_archive(cls, filename: str) -> bool:
        return cls._get_extension(filename) in cls._archive
    
    @staticmethod
    def _get_extension(filename: str) -> str:
        return os.path.splitext(filename)[1]



