# -*- coding: utf-8 -*-

import pollirio.paths as paths
from sqlalchemy import *

def db_init(table):
    """Return a Table object to be used by plugins"""
    db = create_engine("sqlite:///" + paths.dbpath)
    metadata = MetaData(db)
    return Table(table, metadata, autoload=True)

def run(statement):
    """Executes a sqlalchemy statement"""
    return statement.execute()
