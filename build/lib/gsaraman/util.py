#import os
#import cv2
#import numpy as np
#from PIL import Image
from PyQt5 import QtGui, QtCore, QtWidgets
#import pandas as pd
#import copy
#import operator
#import requests
import traceback
import inspect
#from mlxtend.frequent_patterns import apriori
import functools
import logging
#from sqlalchemy import String, Integer, Float, Numeric, Date
#from collections.abc import Sequence
#from collections import OrderedDict, deque
#import pyqtgraph as pg
#from util.gwidgets import LabelMaker, SpacerMaker, BasicLabel, SubheaderLabel, HeaderLabel, MaxSpacer

logger = logging.getLogger(__name__)


def errorCheck(success_text=None, error_text="Error!",logging=True,show_traceback=False,skip=False):
    """
    Decorator for class functions to catch errors and display a dialog box for a success or error.
    Checks if method is a bound method in order to properly handle parents for dialog box.

    success_text:               (str) What header to show in the dialog box when there is no error. None displays no dialog box at all.
    error_text:                 (str) What header to show in the dialog box when there is an error.
    logging:                    (bool) Whether to write error to log. True writes to log, False does not.
    show_traceback:             (bool) Whether to display full traceback in error dialog box. 
    skip:                       (bool) Whether to skip errorCheck. Useful for testing.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if inspect.ismethod(func):
                self = args[0]
            else:
                self = None
            if skip:
                return func(*args, **kwargs)
            try:
                return func(*args, **kwargs)
                if success_text:
                    success_dialog = QtWidgets.QMessageBox(self)
                    success_dialog.setText(success_text)
                    success_dialog.setWindowModality(QtCore.Qt.WindowModal)
                    success_dialog.exec()
            except Exception as e:
                error_dialog = QtWidgets.QMessageBox(self)
                error_dialog.setWindowModality(QtCore.Qt.WindowModal)
                error_dialog.setText(error_text)
                if logging:
                    logger.exception(traceback.format_exc())
                if show_traceback:
                    error_dialog.setInformativeText(traceback.format_exc())
                else:
                    error_dialog.setInformativeText(str(e))
                error_dialog.exec()

        return wrapper
    return decorator