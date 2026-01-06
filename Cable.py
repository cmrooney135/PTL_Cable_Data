
from typing import Optional

import pandas as pd
class Cable: 

    
    def __init__(self, serial_number: str, length: float):
        self.serial_number: str = serial_number
        self.length: float = length

        # Initialize all DataFrame attributes to None
        self.leakage: Optional[pd.DataFrame] = None
        self.leakage_1s: Optional[pd.DataFrame] = None
        self.resistance: Optional[pd.DataFrame] = None
        self.inv_resistance: Optional[pd.DataFrame] = None
        self.continuity: Optional[pd.DataFrame] = None
        self.inv_continuity: Optional[pd.DataFrame] = None


    def add_df(self, type: str, df:pd.DataFrame)->None:
        if(type == "Leakage"):
            self.leakage = df
        elif(type == "1s Leakage"):
            self.leakage_1s = df
        elif(type == "Resistance"):
            self.resistance = df
        elif(type == "Inv Resistance"):
            self.inv_resistance = df
        elif(type == "Continuity"):
            self.continuity = df
        elif(type == "Inv Continuity"):
            self.inv_continuity = df\
        
