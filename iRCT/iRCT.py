import pandas as pd
import numpy as np
import math
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LogisticRegression as lr

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn import metrics

class iRCT:
    def __init__(self, dataframe, treatmentCol, outcomeCol, excludedColumns):
        self.df = dataframe
        self.treatmentCol = treatmentCol
        self.covariateCol = 'propensity_score_logit'
        self.indexCol = self.df.index
        self.outcomeCol = outcomeCol
        self.excludedColumns = excludedColumns
        self.relationVal = self.calculateRelationVal()

    def calculateRelationVal(self):
        """
        :param self: the instance of the iRCT class
        Returns the value calculated using the matching estimators method
        """

        # Creates matches column for matching estimators
        emptyVal = [0] * self.df.index
        self.df.insert(len(self.df.columns), 'matches', emptyVal)
        self.df.drop(columns=self.excludedColumns, inplace=True)

        self.df = self.generatePropensityScores()

        # Finds the closest match/matches in terms of covariate (i.e. propensity_score_logit) values that has the opposite treatment value
        for i in range(len(self.df)):
            print(i)
            base = self.df.iloc[i]
            dfOfMatches = self.df.iloc[(
                self.df[self.covariateCol]-base[self.covariateCol]).abs().argsort()[:]]

            #Very rough pseudo-approach to changing treatment column to binary
            #Essentially each entry will just look for entries where the treatment is different from itself, but the closest matches
            #Since the treatment column is not directly translated to binary there could be some confounding issues
            dfOfMatches = dfOfMatches[dfOfMatches[self.treatmentCol]
                                      != base[self.treatmentCol]]
            temp = abs(dfOfMatches.iloc[0][self.covariateCol]-base[self.covariateCol])
            

            listOfMatches = []

            searchVal = base[self.covariateCol]
            covariateVal = self.df[self.covariateCol]
            queryResult = dfOfMatches.query(
                '@covariateVal-@searchVal == @temp | @searchVal-@covariateVal == @temp').index
            for x in queryResult:
                listOfMatches.append(int(x))

            finalMatches = str(listOfMatches).replace('[', '')
            finalMatches = finalMatches.replace(']', '')

            self.df.at[i, 'matches'] = str(finalMatches)

        # Finds the difference between the matches' average outcome and the current index's outcome, then finds the average of adding all those differences together
        total = 0
        nonNanVals = 0
        for i in range(len(self.df)):
            treat = self.df.iloc[i][self.treatmentCol]
            outcomeValue = self.df.iloc[i]['outcome']
            if type(self.df.iloc[i]['matches']) == str:
                indexMatches = self.df.iloc[i]['matches'].split(",")
            indexMatches = [int(j) for j in indexMatches]

            outcomeMatch = self.df.loc[(self.df.index.isin(
                indexMatches))]['outcome'].mean()

            if treat == 0:
                finalOutcome = outcomeMatch - outcomeValue
            else:
                finalOutcome = outcomeValue - outcomeMatch
            if not math.isnan(finalOutcome):
                total = total + finalOutcome
                nonNanVals = nonNanVals + 1

        return total/nonNanVals  


    def generatePropensityScores(self):
        '''
        :param self: the instance of the iRCT class
        Returns the new dataset with the propensity_score and propensity_score_logit columns

        This function is based on this notebook: https://github.com/konosp/propensity-score-matching/blob/main/propensity_score_matching_v2.ipynb
        '''

        #Define the treatment and outcome columns
        y = self.df[[self.outcomeCol]]
        dfWithoutOutcome = self.df.drop(columns=[self.outcomeCol])
        T = dfWithoutOutcome[self.treatmentCol]

        #Define X or the dataframe for all covariates and fit to a logistical regression model
        X = dfWithoutOutcome.loc[:, dfWithoutOutcome.columns != self.treatmentCol]
        pipe = Pipeline([('scaler', StandardScaler()), ('logistic_classifier', lr())])
        pipe.fit(X, T)

        #Generate the propensity scores
        predictions = pipe.predict_proba(X)
        predictions_binary = pipe.predict(X)

        #Generate the propensity score logit
        predictions_logit = np.array([logit(xi) for xi in predictions[:,1]])

        #Add both propensity_score, propensity_score_logit, and outcome columns to dataframe 
        dfWithoutOutcome.loc[:, 'propensity_score'] = predictions[:,1]
        dfWithoutOutcome.loc[:, 'propensity_score_logit'] = predictions_logit
        dfWithoutOutcome.loc[:, 'outcome'] = y[self.outcomeCol]
        return dfWithoutOutcome


    def FirstAttempt_calculateRelationVal(self):
        """
        :param self: the instance of the iRCT class
        Returns the value calculated using the matching estimators method
        """

        # Organizes dataframe
        self.df.set_index([self.indexCol])

        # Creates matches column for matching estimators
        emptyVal = [0] * self.df.index
        self.df.insert(len(self.df.columns), 'matches', emptyVal)
        self.df.set_index([self.indexCol])

        # Finds the closest match/matches in terms of covariate values that has the opposite treatment value
        for i in range(len(self.df)):
            base = self.df.iloc[i]
            dfOfMatches = self.df.iloc[(
                self.df[self.covariateCol]-base[self.covariateCol]).abs().argsort()[:]]
            dfOfMatches = dfOfMatches[dfOfMatches[self.treatmentCol]
                                      != base[self.treatmentCol]]
            temp = abs(
                (int(dfOfMatches.iloc[0][self.covariateCol])-int(base[self.covariateCol])))

            listOfMatches = []

            searchVal = int(base[self.covariateCol])
            covariateVal = self.df[self.covariateCol]
            queryResult = dfOfMatches.query(
                '@covariateVal-@searchVal == @temp | @searchVal-@covariateVal == @temp')['i']
            for x in queryResult:
                listOfMatches.append(int(x))

            finalMatches = str(listOfMatches).replace('[', '')
            finalMatches = finalMatches.replace(']', '')

            self.df.at[i, 'matches'] = finalMatches

        # Finds the difference between the matches' average outcome and the current index's outcome, then finds the average of adding all those differences together
        total = 0
        for i in range(len(self.df)):
            treat = int(self.df.iloc[i][self.treatmentCol])
            outcomeValue = int(self.df.iloc[i][self.outcomeCol])
            indexMatches = self.df.iloc[i]['matches'].split(",")
            indexMatches = [eval(j) for j in indexMatches]

            outcomeMatch = self.df.loc[(self.df[self.indexCol].isin(
                indexMatches))][self.outcomeCol].mean()

            if treat == 0:
                finalOutcome = outcomeMatch - outcomeValue
            else:
                finalOutcome = outcomeValue - outcomeMatch
            total = total + finalOutcome

        return total/len(self.df)

    def SecondAttempt_CalculateRelationVal(self):
         # Creates matches column for matching estimators
        emptyVal = [0] * self.df.index
        self.df.insert(len(self.df.columns), 'matches', emptyVal)

        self.df = self.generatePropensityScores()

        # Finds the closest match/matches in terms of covariate (i.e. propensity_score_logit) values that has the opposite treatment value
        for i in range(len(self.df)):
            base = self.df.iloc[i]
            dfOfMatches = self.df.iloc[(
                self.df[self.covariateCol]-base[self.covariateCol]).abs().argsort()[:]]
            dfOfMatches = dfOfMatches[dfOfMatches[self.treatmentCol]
                                      != base[self.treatmentCol]]
            temp = abs(dfOfMatches.iloc[0][self.covariateCol]-base[self.covariateCol])


            listOfMatches = []

            searchVal = base[self.covariateCol]
            covariateVal = self.df[self.covariateCol]
            queryResult = dfOfMatches.query(
                '@covariateVal-@searchVal == @temp | @searchVal-@covariateVal == @temp').index
            for x in queryResult:
                listOfMatches.append(int(x))

            finalMatches = str(listOfMatches).replace('[', '')
            finalMatches = finalMatches.replace(']', '')

            self.df.at[i, 'matches'] = str(finalMatches)

        # Finds the difference between the matches' average outcome and the current index's outcome, then finds the average of adding all those differences together
        total = 0
        nonNanVals = 0
        for i in range(len(self.df)):
            treat = self.df.iloc[i][self.treatmentCol]
            outcomeValue = self.df.iloc[i]['outcome']
            if type(self.df.iloc[i]['matches']) == str:
                indexMatches = self.df.iloc[i]['matches'].split(",")
            indexMatches = [int(j) for j in indexMatches]

            outcomeMatch = self.df.loc[(self.df.index.isin(
                indexMatches))]['outcome'].mean()

            if treat == 0:
                finalOutcome = outcomeMatch - outcomeValue
            else:
                finalOutcome = outcomeValue - outcomeMatch
            if not math.isnan(finalOutcome):
                total = total + finalOutcome
                nonNanVals = nonNanVals + 1

        return 1-(total/nonNanVals)   


    def generatePropensityScores(self):
        '''
        :param self: the instance of the iRCT class
        Returns the new dataset with the propensity_score and propensity_score_logit columns
        This function is based on this notebook: https://github.com/konosp/propensity-score-matching/blob/main/propensity_score_matching_v2.ipynb
        '''

        #Define the treatment and outcome columns
        y = self.df[[self.outcomeCol]]
        dfWithoutOutcome = self.df.drop(columns=[self.outcomeCol])
        T = dfWithoutOutcome[self.treatmentCol]

        #Define X or the dataframe for all covariates and fit to a logistical regression model
        X = dfWithoutOutcome.loc[:, dfWithoutOutcome.columns != self.treatmentCol]
        pipe = Pipeline([('scaler', StandardScaler()), ('logistic_classifier', lr())])
        pipe.fit(X, T)

        #Generate the propensity scores
        predictions = pipe.predict_proba(X)
        predictions_binary = pipe.predict(X)

        #Generate the propensity score logit
        predictions_logit = np.array([logit(xi) for xi in predictions[:,1]])

        #Add both propensity_score, propensity_score_logit, and outcome columns to dataframe 
        dfWithoutOutcome.loc[:, 'propensity_score'] = predictions[:,1]
        dfWithoutOutcome.loc[:, 'propensity_score_logit'] = predictions_logit
        dfWithoutOutcome.loc[:, 'outcome'] = y[self.outcomeCol]
        return dfWithoutOutcome

def logit(p):
    logit_value = math.log(p / (1-p))
    return logit_value




