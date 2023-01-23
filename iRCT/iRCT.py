import pandas as pd
import numpy as np
import math
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import time

from sklearn.linear_model import LogisticRegression as lr

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn import metrics

class iRCT:
    def __init__(self, dataframe, treatmentCol, outcomeCol):
        self.df = dataframe
        self.treatmentCol = treatmentCol
        self.covariateCol = 'propensityScoreLogit'
        self.indexCol = self.df.index
        self.outcomeCol = outcomeCol
        self.relationVal, self.timeToComplete = self.calculateRelationVal()

    def calculateRelationVal(self):

        '''
        This function is based on this notebook: https://github.com/konosp/propensity-score-matching/blob/main/propensity_score_matching_v2.ipynb
        '''

        start = time.time()

        # Creates matches column for matching estimators
        emptyVal = [0] * self.df.index
        self.df.insert(len(self.df.columns), 'matches', emptyVal)

        self.df, X = self.generatePropensityScores()

        knn = NearestNeighbors(n_neighbors=5, p=2)
        knn.fit(X[['propensityScoreLogit']].to_numpy())

        distances, indexes = knn.kneighbors(X[['propensityScoreLogit']].to_numpy(), n_neighbors=5)

        def matching(row, indexes, X):
            current_index = int(row['index'])-1
            prop_score_logit = row['propensityScoreLogit']
            for idx in indexes[current_index,:]:
                if (current_index != idx) and (row.treatment == 1) and (X.loc[idx].treatment == 0):
                    return int(idx)

        X['match'] = X.reset_index().apply(matching, axis = 1, args = (indexes, X))
        treated_with_match = ~X.match.isna()
        treated_matched_data = X[treated_with_match][X.columns]
        
        untreated_matched_data = pd.DataFrame(data = treated_matched_data.match)
        untreated_matched_data = untreated_matched_data.set_index('match')

        all_matched_data = pd.concat([treated_matched_data, untreated_matched_data])
        
        overview = all_matched_data[['outcome','treatment']].groupby(by = ['treatment']).aggregate([np.mean, np.var, np.std, 'count'])
        
        treated_outcome = overview['outcome']['mean'][1]
        treated_counterfactual_outcome = overview['outcome']['mean'][0]

        return treated_outcome - treated_counterfactual_outcome, time.time()-start  


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

        X.loc[:, 'propensityScore'] = predictions[:,1]
        X.loc[:, 'propensityScoreLogit'] = predictions_logit
        X.loc[:, 'outcome'] = y[self.outcomeCol]
        X.loc[:, 'treatment'] = dfWithoutOutcome[self.treatmentCol]
        return dfWithoutOutcome, X




    #LEGACY METHOD
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




    #LEGACY METHOD
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


    def SecondAttempt_generatePropensityScores(self):
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




