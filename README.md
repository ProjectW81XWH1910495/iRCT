# iRCT
**i**RCT (intelligent **R**andomized **C**ontrol **T**rial) is a collection of algorithms that can be used to learn causes of an outcome variable using real-world evidence. Currently it includes propensity scoring, matching estimators, and average treatment effect etc methods for estimating causal strength.

Dependencies:
- Pandas

### For any examples shown:

The dataset used can be found in the datasets folder and is name COVID3_4Nodes3.dat.

## Functions and Examples

<br/>

### iRCT.calculateRelationVal

Parameters: The iRCT object

Return values: The output of the respective function and the float representing the time to execute in seconds.

This function selects from the multiple different functions available and returns their outputs as well as the time to run the function.

NOTE: This method is much faster than the other methods due to a much more efficient non-iterative matching approach being used.

</br>

### iRCT.iRCT

Parameters: The iRCT object

Return value: A float value representing the average treatment effect of the treatment column on the outcome column

This function uses propensity scoring in order to match on and then calculating a weight in order to balance the number of treated versus untreated entries. This weight is then multiplied to the propensity scores and averaged in order to determine the average treatment effect.

`E[T|P(x)] = E[E[T|P(x),X]|P(x)] = E[P(x)|P(x)] = P(x)`

#### Example:

When using the COVID3_4Nodes3 dataset with the outcome being COVID and treatment being Dyspnea:

`Relation value for Dyspnea: 0.8314818374143667`
`Outcome column was: COVID`

</br>

### iRCT.SecondAttempt_generatePropensityScores

Parameters: The iRCT object

Return value: An updated dataframe containing the propensity_score and propensity_score_logit columns, a second dataframe for matching use

This function is used to combine all the covariates into a single propensity_score column in order to allow for the matching algorithm to be effective.

#### Example:

This function is called within the calculateRelationVal function

`self.df, X = self.generatePropensityScores()`

</br>

### iRCT.SecondAttempt_calculateRelationVal

Parameters: The iRCT object

Return value: A single float indicating the relation between the treatment and the outcome

This function was the second attempt at the iRCT method and introduced using propensity scoring in order to allow for more than one covariate and thus turn all covariates into a single value in order to perform the matching method on them. This method was replaced with the current version due to the methodology for iterating over the pandas dataframe was extremely ineffective and slow.

NOTE: This method is slower due to the search method for matching based on ilocing the entire dataset and then querying the results.

#### Example:

calculateRelationVal is called whenever an iRCT object is initialized and the value is stored in the relationVal variable.

`self.relationVal = self.SecondAttempt_calculateRelationVal()`


</br>

### iRCT.FirstAttempt_calculateRelationVal

Parameters: The iRCT object

Return value: A single float indicating the relation between the treatment and the outcome

This function was the most rudimentary implementation of the iRCT method using a single covariate column and less than 10 rows in order to get a baseline and test the methodology. This method was replaced due to its extremely slow nature and only being able to deal with a single covariate column.

#### Example:

calculateRelationVal is called whenever an iRCT object is initialized and the value is stored in the relationVal variable.

`self.relationVal = self.FirstAttempt_calculateRelationVal()`

</br>

### iRCT.IPTW

Parameters: The iRCT object

Return value: A single float representing the average treatment effect using inverse probability treatment weighting

This function uses the causal inference package in order to estimate propensity scores for the given dataset and then applies inverse probability weighting in order to balance the treated versus untreated values which allows for an accurate average treatment effect.

`E[Y|X,T=1]−E[Y|X,T=0] = E[{Y}/{P(x)}|X,T=1]P(x) - E[{Y}/{(1-P(x))}|X,T=0](1-P(x))`

#### Example:

The output for this function using the COVID3_4Nodes3 dataset with the treatment column being Dyspnea and outcome being COVID looks like:

`Relation value for Dyspnea: 0.7375587910820504`
`Outcome column was: COVID`

</br>

### iRCT.gFormula

Parameters: The iRCT object

Return value: A single float representing the average treatment effect using the gFormula

The g-formula allows the ability to identify the marginal value of the potential outcome for the outcome under treatment. Then it is able to identify the average potential outcome using only the observed.

#### Example:

The output for this function using the COVID3_4Nodes3 dataset with the treatment column being Dyspnea and outcome being COVID looks like:

`Relation value for Dyspnea: 0.6462371574346719`
`Outcome column was: COVID`

</br>

### iRCT.pythonMBIL

Parameters: The iRCT object

Return value: An array of the direct causes for the given outcome column.

For a better description of how MBIL looks check out the [official page](https://github.com/XiaJiang-2/MBIL)

#### Example:

The output for this function using the COVID3_4Nodes3 dataset with the the outcome column being COVID looks like:

TO BE INSERTED ONCE MBIL PACKAGE IS UPDATED AND WORKING!!!


## How to use

This section is to give a simple explanation on how to use the app.py in order to implement iRCT for your own dataset.

1. Determine and set the output file. This will be used to print the relation value between the outcome and treatment variables.
![FileImage](https://user-images.githubusercontent.com/79263753/214995864-f4235c67-8e21-4831-9dba-a3c2de57d7c0.png)

2. Import your dataset via pandas and ensure all values are numeric. In the sample app.py, most of the values are "negative" or "positive", these are then adjusted to be 0 and 1 in order for the propensity scoring to work properly.
![DatasetManipulation](https://user-images.githubusercontent.com/79263753/214996035-9a4a4c26-6fb6-49cd-8634-8d5049d06c95.png)

3. Set the treatment and outcome column names.
4. Create the iRCT object using the above values. The final integer is representative of the function to be called. 1 is the most recent up-to-date function, 2 is the SecondAttempt function found in iRCT, 3 is the FirstAttempt function found in iRCT, 4 is inverse probability weight training, 5 is GFormula, and 6 is the python version of MBIL.
![iRCT image 3](https://user-images.githubusercontent.com/79263753/218617325-25957a53-f872-49ce-a232-ddbfb971530f.png)


5. Save the output of the relation value.

![WriteOutput](https://user-images.githubusercontent.com/79263753/214996263-bef3285d-7a3c-4260-8a08-ea5f2c2ee106.png)

The current app.py has examples of all these 6 steps and can be used as a simple example in order to get started. 

Inside the datasets directory there is a file named TrueDags.docx, this represents the DAG for the COVID dataset and can be used to help interpret the results of the values found in the Output_files directory.
