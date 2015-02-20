# -*- coding: utf-8 -*-
##############################################################################
# Module by Kranbery Techonolgies LLC
# Not for individual resale or redistribution without expressed written permission of Kranbery Technologies LLC
# Created July 21st 2013
##############################################################################

{
    'name': 'Rapid Serial Number Barcode Scan / Large Logistic Movement Tracking',
    'version': '1.2',
    'author': 'Kranbery Technologies LLC',
    'category': 'Warehouse',
    'description': """
Enables Large Stock Movement Tracking
=====================================    
A re-implementation of serial number management and traceability in the system and/or an additional improvement on split into serial numbers function.
The problem is with large-volume moves, the ORM will die trying to process them large stock split into individual serial numbers.
                
This module can do the following: 
________________________________
* Thousands of serial numbers by attaching the list to large-quantity stock and creating a parallel stock move section called Serial Number Tracking.

* Fixes latency at scan time by using a numbered text field for serial number inputs.  You can also paste excel lists easily into the scan box.

* Adds barcode and import box functionality to the conventional serial number split.

* Accelerated import time with modification to ORM create function to reduce overhead for these specialized operations.

* Allows user to scan serial numbers into a text box then translates the serial numbers to the Split serial numbers list.

* Search for duplicates and verify among quantity when scanning is complete and ready to import.

""",                    
    'website': 'http://www.kranbery.com',
    'summary': 'Rapid Serial Number Barcode Scan / Large Logistic Movement Tracking',
    'depends': ['base', 'web', 'stock', 'sale_stock'],
    'data' : [
#        'security/ir.model.access.csv',
        'wizard/msn_wizard.xml',
        'views/stock.xml',
        'report.xml', 

    ],    
    'css': ['static/src/css/jquery-linedtextarea.css'],
    "active": False,
    "installable": True
}
