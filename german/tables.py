""" tables module

A module to handle tables.
"""

import flask_table as ft

class DataTable(object):
    """
    A class used to decribe a table.

    Attributes
    ----------
    columns : list
        The columns in the table.
    table_template : flask_table.table._Table
        The template of the table.
    table : flask_table.table._Table
        The table.
    """

    def __init__(self, columns):

        self.table_template = ft.create_table()

        self.make_columns(columns)

    def make_columns(self, columns):
        """
        Adds the columns to the table.

        Parameters
        ----------
        columns : list
            The columns in the table.
        """

        for col in columns:
            self.table_template.add_column(col, ft.Col(col))

    def add_rows(self, rows):
        """
        Adds the rows to the table.

        Parameters
        ----------
        rows : list
            A list of rows objects.
        """

        self.table = self.table_template(rows)

    def to_html(self):
        """
        Returns the html for the table.

        Returns
        ----------
        string
            The html code to generate the table.
        """

        return self.table.__html__()