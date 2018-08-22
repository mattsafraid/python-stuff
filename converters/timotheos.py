#! python3
# timotheos.py - The converters closest assistant. 
# This file contains helper functions for the converter scripts. 

from re import sub
from openpyxl.utils.cell import get_column_letter

__placeholder = {
    'mysql': ('%s',),
    'sqlite': '?'
}


def beautify(name, separator='', repl='_'):
    """Returns an uppercase string with only words, numbers and separators"""
    pattern = "[^\w\d_{0}]+".format(separator)
    newname = sub(pattern, repl, name)
    newname = newname.strip(repl).upper()
    return newname


def my_create_table_sql(db_name, table_name, header, 
                        types=[], engine='InnoDB'):
    """Returns a string containing a CREATE TABLE statement for MySQL"""
    
    template = """CREATE TABLE IF NOT EXISTS `{db}`.`{tab}` (
      `__ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
      {cols}
      , PRIMARY KEY (`__ID`)
    ) {eng};"""
    
    if len(types) == 0: 
        types = ["TEXT"] * len(header)
    
    z = zip(header, types)
    columns = ["`{}` {}".format(*c) for c in z if c[1] is not None]
    
    return template.format(
        db = db_name,
        tab = table_name,
        cols = ', \n'.join(columns),
        eng = "ENGINE=" + engine
    )


def my_insert_sql(db_name, table_name, header):
    """Returns a string containing an INSERT statement for MySQL"""
    
    template = """INSERT INTO `{db}`.`{tab}` ( {cols} ) VALUES ({val});"""
    return template.format(
        db = db_name,
        tab = table_name, 
        cols = ', '.join( "`{}`".format(c) for c in header ),
        val = ', '.join( __placeholder['mysql'] * len(header) )     
    )


def my_load_sql():
    """Returns a string containing a LOAD DATA INFILE statement for MySQL"""
    pass

def lite_create_table_sql():
    pass

def lite_insert_sql():
    pass


def xls_fix_header(row):
    """Creates a surrogate name for a worksheet column without a header"""
    h = []
    for i in range( len(row) ):
        c = row[i]
        if c.value: 
            h.append( beautify(c.value) )
        else:
            h.append("COLUMN_{0}1".format(get_column_letter(i+1)))
    return tuple(h)


def xls_row_types_mysql(row):
    """Finds the type of each column based on worksheet metadata"""
    
    '''The fields are: Data type, is date, is empty'''
    dflt = 'TEXT'
    tp = { 
        ('s', False, False): 'TEXT', 
        ('n', True,  False): 'DATETIME(0)', 
        ('n', False, False): 'NUMERIC(16,6)' 
    }
    return [tp.get((c.data_type, c.is_date, not c.value) , dflt) for c in row]