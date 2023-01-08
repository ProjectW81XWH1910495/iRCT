# iRCT
iRCT (intelligent Randomized Control Trial) is an algorithm that uses a combination of propensity scoring, matching estimators, and average treatment effect in order to determine whether a factor has a correlative result in the outcome.

Dependencies:
- Pandas

### For any examples shown:

The dataset used can be found in the datasets folder and is name COVID3_4Nodes3.dat.

## Functions and Examples

### iRCT.generatePropensityScores

Parameters: The iRCT object

Return value: An updated dataframe with a new column holding the propensity score values

This function works by combining all variables that are not either the outcome or treatment into a single covariate value that is then later used for the matching estimators aspect.

Reference for the design of this function can be found [here](https://github.com/konosp/propensity-score-matching/blob/main/propensity_score_matching_v2.ipynb)

#### Example:

This function is called by the calculateRelationVal function.

`self.df = self.generatePropensityScores()`

<br/>

### iRCT.calculateRelationVal

Parameters: The iRCT object

Return value: A single float indicating the relation between the treatment and the outcome

This function uses the afforementioned propensity scores to perform a matching estimator method and then finds the average treatment outcome.

#### Example:

calculateRelationVal is called whenever an iRCT object is initialized and the value is stored in the relationVal variable.

`self.relationVal = self.calculateRelationVal()`

When the outcome column was COVID and treatment was Dyspnea the result was:

`Relation value for Dyspnea: 0.7165481689737879`

## How to use

This section is to give a simple explanation on how to use the app.py in order to implement iRCT for your own dataset.

1. Determine and set the output file. This will be used to print the relation value between the outcome and treatment variables.
2. Import your dataset via pandas and ensure all values are numeric. In the sample app.py, most of the values are "negative" or "positive", these are then adjusted to be 0 and 1 in order for the propensity scoring to work properly.
3. Set the treatment and outcome column names.
4. Create a list of any columns that need to be excluded when calculating the propensity score i.e. creating the matches.
5. Create the iRCT object using the above values.
6. Save the output of the relation value.

The current app.py has examples of all these 6 steps and can be used as a simple example in order to get started. 

Inside the datasets directory there is a file named TrueDags.docx, this represents the DAG for the COVID dataset and can be used to help interpret the results of the values found in the Output_files directory.