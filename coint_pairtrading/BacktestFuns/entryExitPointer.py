from entryExitPointer_Dynamic_perEntryMaxProfit import *
from entryExitPointer_Dynamic_perEntryMaxLoss import *


def getEntryExitPointer(option) : 

    match option:

        case 'EntryPoint_MaxProfit' :
            return entryExitPointer_Dynamic_perEntryMaxProfit
        
        case 'EntryPoint_MaxLoss' :
            return entryExitPointer_Dynamic_perEntryMaxLoss
