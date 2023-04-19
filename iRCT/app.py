import pandas as pd
import iRCT


# Read in dataframe with seperators being commas
f = open('C:/Users/17172/Desktop/iRCT/iRCT/Output_files/testOutput-Function2', 'a')

df1 = pd.read_csv("C:/Users/17172/Desktop/iRCT/datasets/COVID3_4Nodes3.txt", sep=",")



for col1 in df1.columns:
    if col1 == 'ED_Visit':
        continue
    for col2 in df1.columns:
        if col2 == col1:
            continue
        if col2 == 'ED_Visit' and col1 == 'Dyspnea':
            continue
        
        df = pd.read_csv("C:/Users/17172/Desktop/iRCT/datasets/COVID3_4Nodes3.txt", sep=",")
        # # Create an index column and and replace all categorical values with numerical values
        df.index = range(1, len(df)+1, 1)
        df = df.replace(to_replace='No', value=0)
        df = df.replace(to_replace='Yes', value=1)
        df = df.replace(to_replace='Negtive', value=0)
        df = df.replace(to_replace='Positive', value=1)

        # Only will be used if functionNum is 3
        singleCovariate = None

        # Create an iRCT object
        # The final integer is the function to be used 1 is the most recent up-to-date function, 2 is the SecondAttempt function found in iRCT, 3 is the FirstAttempt function found in iRCT,
        # 4 is inverse probability weight training, 5 is GFormula, and 6 is the python version of MBIL.
        myiRCT = iRCT.iRCT(df, col2, col1, 2, None)

        print("Completed " + str(col2) + " with outcome column " + str(col1))


        #Write the relation value to the file from above
        f.write("Relation value for " + col2 + ": " + str(myiRCT.relationVal))
        f.write('\n')

        f.write("Outcome column was: " + col1)
        f.write('\n')

        f.write("Time to run was: " + str(myiRCT.runningTime) + " seconds")
        f.write("\n\n")
