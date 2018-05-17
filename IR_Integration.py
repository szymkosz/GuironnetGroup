"""
This code is used to find the area under the curve between two integration bounds.
It is specifically written for the Guironnet Lab at the University of Illinois
for use with the IR spectrometer and the Opus 7.5 spectroscopy software.

Below is a description of how to use it. Select computers in the lab are pre-
configured to be compatible with these instructions as of May 16, 2018.


1.  PLUG-AND-PLAY USE:

    1.1     Open the command prompt.
            Click start and type 'cmd' into the 'Search programs and files' field

    1.2     Navigate to the 'GuironnetGroup' folder using the 'cd' command.
            This folder should be on the Desktop, but may be elsewhere.

            $ cd Desktop/GuironnetGroup

            NOTE: The 'cd' command will not work on all Windows machines because
            it is a Unix command. Select lab computers have been configured such
            that this command (and other Unix commands, including 'ls') will work on them.

    1.3     Get the latest copy of the code by running the command below.

            $ git pull

            1.3.1   If the above command fails, it is likely that the local
                    version of the file differs from the Github version. To
                    override this and to overwrite the local copy with the Github
                    version, run the commands below.

                    WARNING: Any local changes to the file will be lost.

                    $ git fetch
                    $ git checkout IR_Integration.py

    1.4     Run the code using this command. The program assumes that a correctly
            formatted file named 'data.csv' exists (see Section 2). It will create
            a new file titled 'result.csv'.

            $ python IR_Integration.py


2.  INPUT DATA FILE FORMATTING

    There must be a .CSV (Comma-separated Value) file containing the spectroscopy
    data which satisfies the following criteria:

    -   The first row is the header row. Sample IDs go here with the corresponding
        data in the rows below.
    -   The first column contains the x-values (wavenumbers or wavelengths)
    -   Every columns thereafter is a dataset
    -   Every dataset in the file must be of the same size
    -   For each dataset, there must be one data point for each x-value.
    -   Cell A1 may be left empty

    CSV files can be created in Microsoft Excel.
    -   Click File -> Save as
    -   In the 'File Format' or 'Save as type' list, select the .csv file type,
        which might look something like 'CSV UTF-8 (.csv)'

"""

import numpy as np
import matplotlib.pyplot as plt
import csv

## Source and output file names
fileName = "data.csv"
saveFile = "result.csv"     ### This will overwrite any identically-named file

## List of tuples containing integration bounds
intRanges = [(3050, 3725),
            (1550, 1775)]

## Reads data in from the input file
with open(fileName, 'r') as file:
    reader = csv.reader(file)
    headers = next(reader)

## Creates an array containing all of the samples IDs in fileName
headers = headers[1:]
## Compiles data into a numpy array
data = np.genfromtxt(fileName, delimiter=',',skip_header=1)

# Find the index of the value in the dataset closest to input value
def find_nearest(arr, val):
    idx = (np.abs(arr - val)).argmin()
    return idx

"Integrates data over the bound"
def integral(lb, ub):
    if ub < lb:
        temp = lb
        lb = ub
        ub = temp
    idxMin = find_nearest(data[:,0],lb)
    idxMax = find_nearest(data[:,0],ub)

    # print(data[idxMin,0],data[idxMax,0])

    result = (data[idxMax+1:idxMin,1:] + data[idxMax:idxMin-1,1:])/2
    result = np.multiply(np.transpose(result),(data[idxMax:idxMin-1,0] - data[idxMax+1:idxMin,0]))

    return np.sum(result, axis=1)

## Prepares data for writing into CSV output file
resultArr = np.zeros((len(intRanges), len(headers)))
for j in range(len(intRanges)):
    resultArr[j,:] = integral(intRanges[j][0],intRanges[j][1])

## Writes integration results into the output CSV file
with open(saveFile, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
    writer.writerow(headers)
    for i in range(len(intRanges)):
        writer.writerow(resultArr[i,:])

## Prints the integration result into standard output
# for i in range(len(headers)):
#     print("\t%s" % headers[i])
#     print(integral(3050, 3725)[i])
#     print(integral(1550, 1775)[i])
