import pandas as pd

class iRCT:
    def __init__(self, dataframe, treatmentCol, covariateCol, indexCol, outcomeCol):
        self.df = dataframe
        self.treatmentCol = treatmentCol
        self.covariateCol = covariateCol
        self.indexCol = indexCol
        self.outcomeCol = outcomeCol
        self.relationVal = self.calculateRelationVal()

    def calculateRelationVal(self):
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
