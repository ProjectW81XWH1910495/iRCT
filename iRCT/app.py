import pandas as pd
import iRCT


# Read in dataframe with seperators being commas
df = pd.read_csv("C:/Users/17172/Desktop/CausalLearning/sample_data/test.txt")

# Set the name of your treatment column which should be a binary value, your covariate column, your index column, and your outcome column or the name of the variable you are trying to measure
treatmentCol = 'treatment'
covariateCol = 'X'
indexCol = 'i'
outcomeCol = 'Y'


# Create an iRCT object
myiRCT = iRCT.iRCT(df, treatmentCol, covariateCol, indexCol, outcomeCol)


# Print the relation value for your dataset given the above values
print(myiRCT.relationVal)


#For transform function, combine all values of every column (other than index, treatment, and outcome) into a single string per entry
#For each entry compare that string to all other entries and count how many characters are different, the strings with the lowest character difference and opposite treatment value
#will be set as the matching entries
