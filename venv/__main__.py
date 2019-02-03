import os
import pandas as pd
from loguru import logger
import matplotlib.pyplot as plt

import settings

debugging = False
logging = False

""" Step 1: Get a list of files in the folder
Step 2: Iterate through the files
Step 2a: Split the file into columns at commas - Date,Open,High,Low,Close,Volume
Step 2b: Step through each datapoint in the file. If the closing price is *about* 100 smaller than that previous
         close, multiply that closing price with 100.
Step 2c: Save the file with a new prefix."""

def init():
    logger.info("Initializing.")
    debugging = settings.getdebug()

def is_approximate_factor(num1, num2, factor, margin):
    """is_approximate_factor tests if num1*factor is close to num2, within an error margin.
    This is useful in cleaning up financial data where data was saved as the major currency denominator (eg. dollars)
    at some point, and then suddenly as the minor denominator (eg. cents), or vice versa.

    Input arguments:
    num1: The smaller number.
    num2: The larger number.
    factor: The multiplication factor that should be tested.
    margin: The allowed margin of error, in percent of (num1 * factor).

    Example:
        If we want to see if the number 1 is approximately 100 times smaller than the number 99.8, the function would
        be called as:
        result = is_approximate_factor(1, 99.8, 100, 0.5)
        and would return true.
        result = is_approximate_factor(1, 99.4, 100, 0.5)
        would return false, as  (1 * 100) * (100-0.5) > 99.4
    """

    comparenum = num1 * factor

    pctdiff = abs((comparenum - num2) / num2)

    if debugging:
        logger.debug(f"Pct difference: {pctdiff}")

    if pctdiff < margin:
        if debugging:
            logger.debug(f"{num2} is found to be approximately {factor} times {num1} within {margin*100}%.")
        return True
    else:
        if debugging:
            logger.debug(f"{num2} is found to not be approximately {factor} times {num1} within {margin*100}%.")
        return False

if __name__ == "__main__":
    logger.info("Main function started.")

    init()

    limit = settings.iterlimit()

    logger.info("Step 1: Get a list of files in the folder.")

    directories = os.listdir("..\\sourcedata\\")
    if debugging:
        logger.debug(f"{directories}")

    logger.info("Step 2: Iterate through the files")
    for csvfile in directories:
        logger.info("Step 1a: Open the file in read only mode")
        if debugging:
            logger.debug(f"Filename: {csvfile}")
        original_data = pd.read_csv("..\\sourcedata\\" + csvfile)
        # The file is already split by commas

        if debugging:
            logger.debug(original_data["Date"])
            logger.debug(original_data["Open"])
            logger.debug(original_data["High"])
            logger.debug(original_data["Low"])
            logger.debug(original_data["Close"])
            logger.debug(original_data["Volume"])

        # Step 2b: Step through each datapoint in the file IN REVERSE. If the closing price is *about* 100 smaller than
        # that previous close, multiply that closing price with 100.

        # Step through in reverse:
        loopindex = -1
        new_data = original_data.copy()
        error = settings.errormargin()
        for idx in reversed(original_data.index):
            if debugging:
                logger.info(f"Starting for loop over the data from {csvfile}.")

            if debugging:
                logger.debug(f"loopindex: {loopindex}")
                logger.debug(f"{idx}:")

            todayclose = original_data.loc[idx, 'Close']

            # If the closing price at index is about 100 smaller than the closing price at (index - 1), then multiply the
            #  closing price at idx by exactly 100.
            # This is all done in a new dataframe, as we shouldn't change the dataframe we're iterating over.

            # We need to re-index, as idx gets reversed *with* the dataset (ie. runs from high to low)
            loopindex = loopindex + 1
            # This means that idx is the dataset index, and loopindex is the for-loop's index

            # I'm not sure if the volume needs to be adjusted (I don't think so), but Open, High, Low, and Close should.

            # At index = 0 there will be no (index - 1) to query, so skip that special case. Just put the datapoint in
            # the new dataframe
            if loopindex == 0:
                # The new dataframe is already a copy of the previous one, so we don't need to do anything.
                if debugging:
                    logger.info(f"loopindex == {loopindex}, so do nothing!")
            else:
                tomorrowclose = new_data.loc[idx + 1, 'Close']

                # Is close[index - 1] * 100 ~= close[index]?
                if is_approximate_factor(todayclose, tomorrowclose, 100, error):
                    if debugging:
                        logger.info(f"Closing price on {todayclose} found to be approximatey 100 times smaller than the next day's entry. ")

                    new_data.loc[idx, 'Open'] = original_data.loc[idx, 'Open'] * 100
                    new_data.loc[idx, 'High'] = original_data.loc[idx, 'High'] * 100
                    new_data.loc[idx, 'Low'] = original_data.loc[idx, 'Low'] * 100
                    new_data.loc[idx, 'Close'] = original_data.loc[idx, 'Close'] * 100

                    if debugging:
                        logger.debug(f"New Open:  {new_data.loc[idx, 'Open']}")
                        logger.debug(f"New High:  {new_data.loc[idx, 'High']}")
                        logger.debug(f"New Low:   {new_data.loc[idx, 'Low']}")
                        logger.debug(f"New Close: {new_data.loc[idx, 'Close']}")

                elif todayclose == 0:
                    # Special case: todayclose == 0
                    logger.info(f"Price was missing on {original_data.loc[idx, 'Date']}")
                    new_data.loc[idx, 'Open'] = new_data.loc[idx + 1, 'Open']
                    new_data.loc[idx, 'High'] = new_data.loc[idx + 1, 'High']
                    new_data.loc[idx, 'Low'] = new_data.loc[idx + 1, 'Low']
                    new_data.loc[idx, 'Close'] = new_data.loc[idx + 1, 'Close']
                else:
                    if debugging:
                        logger.debug(f"Date: {original_data.loc[idx, 'Date']}")
                        logger.debug(f"todayclose:    {todayclose}")
                        logger.debug(f"tomorrowclose: {tomorrowclose}")
                        logger.debug(f"error margin:  {error}")

        logger.info("Step 2c: Save the file with a new prefix.")
        newfilename =  "..\\data\\" + "fixed-" + csvfile
        if debugging:
            logger.debug(f"Save the results to {newfilename}")
        new_data.to_csv(newfilename, encoding='utf-8')