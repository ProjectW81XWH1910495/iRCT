import pandas as pd
import iRCT


# Read in dataframe with seperators being commas
df_for_loop = pd.read_csv("C:/Users/17172/Desktop/iRCT/datasets/COVID3_4Nodes3.dat")
f = open('C:/Users/17172/Desktop/iRCT/iRCT/Output_files/output_outcomeEDVisit.txt', 'w')

listOfColumns = df_for_loop.columns
outcomeCol = 'ED_Visit'
listOfColumns = listOfColumns.drop(outcomeCol)
listOfColumns = listOfColumns.drop('COVID')
listOfColumns = listOfColumns.drop('Dyspnea')

for column in listOfColumns:
    df = pd.read_csv("C:/Users/17172/Desktop/iRCT/datasets/COVID3_4Nodes3.dat")
    df.index = range(1, len(df)+1, 1)
    df = df.replace(to_replace='No', value=0)
    df = df.replace(to_replace='Yes', value=1)
    df = df.replace(to_replace='Negtive', value=0)
    df = df.replace(to_replace='Positive', value=1)

    # Set the name of your treatment column which should be a binary value, your covariate column, your index column, and your outcome column or the name of the variable you are trying to measure and the columns you want excluded from being used for matching
    treatmentCol = column
    excludedColumns = []

    # Create an iRCT object
    myiRCT = iRCT.iRCT(df, treatmentCol, outcomeCol, excludedColumns)


    #Write the relation value to the file from above
    f.write("Relation value for " + treatmentCol + ": " + str(myiRCT.relationVal))
    f.write('\n')

f.write("Outcome column was: " + outcomeCol)
f.write('\n')
