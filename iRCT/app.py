import pandas as pd
import iRCT


# Read in dataframe with seperators being commas
f = open('C:/Users/17172/Desktop/iRCT/iRCT/Output_files/testOutput', 'a')

df = pd.read_csv("C:/Users/17172/Desktop/iRCT/datasets/COVID3_4Nodes3.txt")

# Create an index column and and replace all categorical values with numerical values
df.index = range(1, len(df)+1, 1)
df = df.replace(to_replace='No', value=0)
df = df.replace(to_replace='Yes', value=1)
df = df.replace(to_replace='Negtive', value=0)
df = df.replace(to_replace='Positive', value=1)

# Set the name of your treatment column which should be a binary value and your outcome column or the name of the variable you are trying to measure
treatmentCol = 'Dyspnea'
outcomeCol = 'COVID'

# Only will be used if functionNum is 3
singleCovariate = None

# Create an iRCT object
# The final integer is the function to be used 1 = the most recent up-to-date function, 2 is the SecondAttempt function found in iRCT, and 3 is the FirstAttempt function found in iRCT.
myiRCT = iRCT.iRCT(df, treatmentCol, outcomeCol, 1, None)


#Write the relation value to the file from above
f.write("Relation value for " + treatmentCol + ": " + str(myiRCT.relationVal))
f.write('\n')

f.write("Outcome column was: " + outcomeCol)
f.write('\n')
