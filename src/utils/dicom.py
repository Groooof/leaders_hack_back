import pydicom
import matplotlib.pyplot as plt

def dicom_to_image(path_to_dicom, path_to_save):
    ds = pydicom.dcmread(path_to_dicom)
    plt.imsave(path_to_save, ds.pixel_array, cmap=plt.bone())
    return path_to_save


def remove_patient_personal_data(path_to_dicom):
    ds = pydicom.dcmread(path_to_dicom)
    ds.PatientName = None
    ds.PatientID = None
    ds.PatientSex = None
    ds.PatientBirthDate = None
    ds.PatientIdentityRemoved = 'YES'
    ds.save_as(path_to_dicom)    
    
