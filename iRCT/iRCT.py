import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import time
from causalinference import CausalModel
from zepid.causal.gformula import TimeFixedGFormula
from psmpy import PsmPy
from psmpy.functions import cohenD
from psmpy.plotting import *

from sklearn.linear_model import LogisticRegression

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn import metrics

from mbil import scores
from mbil import dataset
from mbil import mbilsearch
from mbil import mbilscore
from mbil import output

class iRCT:
    def __init__(self, dataframe, treatmentCol, outcomeCol, functionNum, singleCovariate):
        self.df = dataframe
        self.treatmentCol = treatmentCol
        self.covariateCol = 'propensity_score_logit'
        self.indexCol = self.df.index
        self.outcomeCol = outcomeCol
        self.functionNum = functionNum
        self.singleCovariate = singleCovariate
        self.relationVal, self.runningTime = self.calculateRelationVal()

    def calculateRelationVal(self):

        finalVal = 0.0
        if int(self.functionNum) == 1:
            startTime = time.time()
            finalVal = self.iRCT()
            return finalVal, time.time() - startTime
        elif int(self.functionNum) == 2:
            startTime = time.time()
            finalVal = self.SecondAttempt_CalculateRelationVal()
            return finalVal, time.time() - startTime
        elif int(self.functionNum) == 3:
            startTime = time.time()
            finalVal = self.FirstAttempt_calculateRelationVal()
            return finalVal, time.time() - startTime
        elif int(self.functionNum) == 4:
            startTime = time.time()
            finalVal = self.IPTW()
            return finalVal, time.time() - startTime
        elif int(self.functionNum) == 5:
            startTime = time.time()
            finalVal = self.gFormula()
            return finalVal, time.time() - startTime
        elif int(self.functionNum) == 6:
            startTime = time.time()
            finalVal = self.pythonMBIL()
            return finalVal, time.time() - startTime
        
    

    def iRCT(self):
        '''
        Uses matching in order to determine the average treatment effect via https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/user-guide/Treatment-Effects
        '''

        T = self.treatmentCol
        Y = self.outcomeCol
        X = self.df.columns.drop([T, Y])

        ps_model = LogisticRegression(C=1e6).fit(self.df[X], self.df[T])
        data_ps = self.df.assign(propensity_score=ps_model.predict_proba(self.df[X])[:, 1])

        weight = ((data_ps[self.treatmentCol]) / (data_ps["propensity_score"]))

        ate = np.mean(weight * data_ps[self.outcomeCol])
        return ate
    


    #Old method
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
                self.df[self.singleCovariate]-base[self.singleCovariate]).abs().argsort()[:]]
            dfOfMatches = dfOfMatches[dfOfMatches[self.treatmentCol]
                                      != base[self.treatmentCol]]
            temp = abs(
                (int(dfOfMatches.iloc[0][self.singleCovariate])-int(base[self.singleCovariate])))

            listOfMatches = []

            searchVal = int(base[self.singleCovariate])
            covariateVal = self.df[self.singleCovariate]
            queryResult = dfOfMatches.query(
                '@covariateVal-@searchVal == @temp | @searchVal-@covariateVal == @temp')
            queryResult = queryResult.index.tolist()
            for x in queryResult:
                listOfMatches.append(int(x))

            finalMatches = str(listOfMatches).replace('[', '')
            finalMatches = finalMatches.replace(']', '')

            self.df.at[i+1, 'matches'] = finalMatches

        # Finds the difference between the matches' average outcome and the current index's outcome, then finds the average of adding all those differences together
        total = 0
        for i in range(len(self.df)):
            treat = int(self.df.iloc[i][self.treatmentCol])
            outcomeValue = int(self.df.iloc[i][self.outcomeCol])
            indexMatches = self.df.iloc[i]['matches'].split(",")
            indexMatches = [eval(j) for j in indexMatches]

            outcomeMatch = self.df.loc[(self.df.index.isin(indexMatches))][self.outcomeCol].mean()

            if treat == 0:
                finalOutcome = outcomeMatch - outcomeValue
            else:
                finalOutcome = outcomeValue - outcomeMatch
            total = total + finalOutcome

        return total/len(self.df)



    #Old Methods
    def SecondAttempt_CalculateRelationVal(self):
         # Creates matches column for matching estimators
        emptyVal = [0] * self.df.index
        self.df.insert(len(self.df.columns), 'matches', emptyVal)

        self.df = self.SecondAttempt_generatePropensityScores()

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
        pipe = Pipeline([('scaler', StandardScaler()), ('logistic_classifier', LogisticRegression())])
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


    
    def IPTW(self):
        '''
        This method is based of the example from https://medium.com/grabngoinfo/inverse-probability-treatment-weighting-iptw-using-python-package-causal-inference-7d8f454eb8f3
        '''
        cols = list(self.df.columns)
        cols.remove(self.outcomeCol)
        cols.remove(self.treatmentCol)

        causal = CausalModel(Y = self.df[self.outcomeCol].values, D = self.df[self.treatmentCol].values, X = self.df[cols].values)

        causal.est_propensity_s()
        causal.est_via_weighting()

        return causal.estimates.get('weighting').get('ate')
    
    def gFormula(self):

        '''
        This code is based on the code here: https://github.com/pzivich/Python-for-Epidemiologists/blob/master/3_Epidemiology_Analysis/c_causal_inference/1_time-fixed-treatments/01_g-formula.ipynb
        '''

        g = TimeFixedGFormula(self.df, exposure=self.treatmentCol ,outcome=self.outcomeCol)

        base = ''

        listColumns = list(self.df.columns)
        listColumns.remove(self.outcomeCol)
        for column in listColumns:
            base += column + " + "

        base = base[:len(base)-3]

        g.outcome_model(model = base, print_results=False)

        g.fit(treatment='all')
        r_all = g.marginal_outcome

        g.fit(treatment='none')
        r_none = g.marginal_outcome

        return r_all - r_none
    

    def pythonMBIL(self):
        alpha = 4
        target = self.outcomeCol
        top = 20
        max_single_predictors = 20
        max_interaction_predictors = 20
        max_size_interaction = 3
        threshold = 0.05
        maximum_number_of_parents=7

        score_test_obj = mbilscore.mbilscore(dataset_df=self.df, target=target, alpha = alpha)
        search_test_object = mbilsearch.mbilsearch(threshold=threshold,
                                                max_single_predictors= max_single_predictors,
                                                max_interaction_predictors=max_interaction_predictors,
                                                max_size_interaction= max_size_interaction,
                                                dataset_df = self.df,
                                                alpha = alpha,
                                                target = target)
        
        direct_cause_obj = mbilsearch.directCause(
            new_dataset = search_test_object.transformed_dataset,
            alpha= alpha,
            target = target,
            maximum_number_of_parents = maximum_number_of_parents)
        
        return direct_cause_obj.direc_cause

def logit(p):
    logit_value = math.log(p / (1-p))
    return logit_value