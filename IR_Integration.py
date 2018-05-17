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

    #print(data[idxMin,0],data[idxMax,0])

    result = (data[idxMax+1:idxMin,1:] + data[idxMax:idxMin-1,1:])/2
    result = np.multiply(np.transpose(result),(data[idxMax:idxMin-1,0] - data[idxMax+1:idxMin,0]))

    return np.sum(result, axis=1)

## Prepares data for writing into CSV output file
resultArr = np.zeros((len(intRanges), len(headers)))
for j in range(len(intRanges)):
    resultArr[j,:] = integral(intRanges[j][0],intRanges[j][1])

"Writes integration results into the output CSV file"
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
