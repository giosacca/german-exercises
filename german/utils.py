"""utils module

A module that contains useful functions.
"""

import unidecode

def get_sort_value(expression):
    """
    Returns the sorting value.

    Returns
    ----------
    string
        The string to be used to sort.
    """
    
    import unidecode
    
    expression = expression.lower()
    expression = unidecode.unidecode(expression)
    expression = remove_sich(expression)
    expression = remove_article(expression)
    expression = remove_apostrophe(expression)
    
    return expression
    
def remove_article(expression):
    """
    Removes the articles at the beginning of the string.

    Returns
    ----------
    string
        The string without an article in the beginning.
    """
    
    articles = ['der ', 'die ', 'das ']
    
    if expression[0:4] in articles:
        expression = expression[4:]
        
    return expression

def remove_sich(expression):
    """
    Removes the sich at the beginning of the string.

    Returns
    ----------
    string
        The string without a sich in the beginning.
    """
    
    if expression[0:5] == 'sich ':
        expression = expression[5:]
        
    return expression

def remove_apostrophe(expression):
    """
    Removes the apostrophes from the string.

    Returns
    ----------
    string
        The string without apostrophes.
    """
    
    expression = expression.replace("'", '')
        
    return expression