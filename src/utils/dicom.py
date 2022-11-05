import pydicom
import matplotlib.pyplot as plt


def dicom_to_image(path_to_dicom, path_to_save):
    ds = pydicom.dcmread(path_to_dicom)
    plt.imsave(path_to_save, ds.pixel_array, cmap=plt.bone())
    return path_to_save

