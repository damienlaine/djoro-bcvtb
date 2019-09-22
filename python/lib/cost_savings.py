# -*- coding: utf-8 -*-
"""
Created on Sat Aug 30 18:58:00 2014

@author: perez
"""

from db_connection import *
from config import *
import datetime

class Cost_Savings:
    """ Contains methods for cost savings calculation """
    def __init__(self):
        pass

    # Update the real cost savings
    @staticmethod    
    def real_money_saved_calc(siteId, deviceId):
        # Get the device in the database
        device = MongoConnection.getDevice(siteId, deviceId)
        # Get the last element of money saved
        money_saved = device['money_saved'][len(device['money_saved']) - 1]
        now = datetime.datetime.utcnow()
        # If this is the first time we calculate the savings, we will just update the date. No calculation.
        if money_saved['last_calc_date'] is None:
            pass
        else:
            # Get base temperature
            base_temp = device['base_temp']
            # Calculate number of days since last calculation
            timedelta = now - money_saved['last_calc_date']
            deltadays = timedelta.days + (float(timedelta.seconds) / 86400)
            # Get the cost of a DJU
            dju_cost = device['dju_cost']
            # Get the measured temperature
            setpoint = device['history'][len(device['history']) - 1]['measuredTemp']
            # Calculate new cost savings
            new_cost_savings = max ((base_temp - setpoint) , 0) * deltadays * dju_cost
            # Update total cost savings
            money_saved['amount'] += new_cost_savings
            
        # Update last_calc_date
        money_saved['last_calc_date'] = now
        
        # Put the calculated cost savings in the database
        device['money_saved'][len(device['money_saved']) - 1] = money_saved
        MongoConnection.updateMoneySaved(siteId, deviceId, device['money_saved'])
        
        return money_saved['amount']
        