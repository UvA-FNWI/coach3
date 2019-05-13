import pandas as pd

def load_access_file():
    access_df = pd.read_csv('access_and_data_rights.csv')
    return access_df

def has_access(email):
    access_df = load_access_file()
    if email in access_df['email'].values:
        student_rights = access_df[access_df['email']==email]
        if student_rights['type'].values == 'test':
            return True
    return  False

def can_use_data(email):
    access_df = load_access_file()
    if email in access_df['email'].values:
        student_access = access_df[access_df['email']==email]
        if student_access['access'].values == 'y':
            return True
    return False