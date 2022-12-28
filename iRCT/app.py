import pandas as pd
import iRCT


# Read in dataframe with seperators being commas
df = pd.read_csv("C:/Users/17172/Desktop/iRCT/datasets/LSM-15Year.txt", sep='\t')
f = open('C:/Users/17172/Desktop/iRCT/iRCT/output.txt', 'w')

outcomeCol = 'distant_recurrence'

newDF = pd.read_csv("C:/Users/17172/Desktop/iRCT/datasets/LSM-15Year.txt", sep='\t')
newDF.index = range(1, len(df)+1, 1)

# Set the name of your treatment column which should be a binary value, your covariate column, your index column, and your outcome column or the name of the variable you are trying to measure and the columns you want excluded from being used for matching
treatmentCol = 'menopause_status'
excludedColumns = []

# Create an iRCT object
myiRCT = iRCT.iRCT(newDF, treatmentCol, outcomeCol, excludedColumns)


# Print the relation value for your dataset given the above values
f.write("Relation value for " + treatmentCol + ": " + str(myiRCT.relationVal))
f.write('\n')
