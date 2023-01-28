import pandas as pd
import iRCT


# Read in dataframe with seperators being commas
f = open('/Users/xij6/Documents/Research/git/XiaJiang-2Github/iRCT/iRCT/Output_files/jiang_tests_output.txt', 'a')

df = pd.read_csv("/Users/xij6/Documents/Research/git/XiaJiang-2Github/iRCT/datasets/COVID3_4Nodes3.dat")

# Create an index column and and replace all categorical values with numerical values
df.index = range(1, len(df)+1, 1)
df = df.replace(to_replace='No', value=0)
df = df.replace(to_replace='Yes', value=1)
df = df.replace(to_replace='Negtive', value=0)
df = df.replace(to_replace='Positive', value=1)

# Set the name of your treatment column which should be a binary value and your outcome column or the name of the variable you are trying to measure
treatmentCol = 'Dyspnea'
outcomeCol = 'COVID'

# Create an iRCT object
myiRCT = iRCT.iRCT(df, treatmentCol, outcomeCol)


#Write the relation value to the file from above
f.write("Relation value for " + treatmentCol + ": " + str(myiRCT.relationVal))
f.write('\n')

f.write("Outcome column was: " + outcomeCol)
f.write('\n')
