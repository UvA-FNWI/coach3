import pandas as pd
from django.conf import settings

def load_access_file():
    """
    loads the access csv file, which includes, the email addresses, whether they can use the tool (i.e. are participants)
    and whether we can use their data to generate the comparison group.
    :return: the access file as a pandas dataframe.
    """
    access_df = pd.read_csv(settings.FILES_DIR+'access_and_data_rights.csv')
    return access_df

def has_access(email):
    """
    Checks if the user with the given email has access to the tool.
    :param email: the email address of the user.
    :return: True is the user has access, False otherwise.
    """
    access_df = load_access_file()
    if email in access_df['email'].values:
        student_rights = access_df[access_df['email']==email]
        if student_rights['type'].values == 'test':
            return True
    return  False

def can_use_data(email):
    """
    Checks if the data of a student can be used to generate the comparison set.
    :param email: the email address of the user.
    :return: True if the data can be used, False otherwise.
    """
    access_df = load_access_file()
    if email in access_df['email'].values:
        student_access = access_df[access_df['email']==email]
        if student_access['access'].values == 'y':
            return True
    return False