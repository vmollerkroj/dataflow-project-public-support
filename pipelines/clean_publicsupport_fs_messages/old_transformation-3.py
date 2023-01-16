import pandas as pd
import numpy as np
from datetime import datetime


def run(df):
    """
    This function creates a dataframe only for questions.
    """

    print('Shape before creating new questions_df', df.shape)

    Q_df = df[df['Is_a_question'] == 1]

    questions = Q_df.groupby(['User_ID','Datetime'])[['Text']]
    df_questions = pd.DataFrame(questions.sum().reset_index())

    df_questions['Diff_in_Seconds'] = (df_questions.sort_values('Datetime').groupby('User_ID').Datetime.diff())

    df_questions['Diff_in_Seconds'] = df_questions['Diff_in_Seconds'].fillna(pd.Timedelta(seconds=0))

    df_questions['Diff_in_Seconds'] = df_questions['Diff_in_Seconds']/np.timedelta64(1,'s')

    df_questions['diff_abs'] = df_questions.Diff_in_Seconds.abs()

    df_questions['same_author'] = df_questions['User_ID'].ne(df_questions['User_ID'].shift().bfill()).astype(int)

    def create_QuestionId(dfx):
        for group in dfx.groupby(['User_ID']):
            dfx['messageId'] = dfx['diff_abs'].gt(300).cumsum() + 1 + dfx.same_author.cumsum()
        return dfx

    create_QuestionId(df_questions)


    #Merge dataframe to its previous columns
    df_questions = df_questions.merge(Q_df, how = 'left', left_on = ['User_ID', 'Datetime', 'Text'],
    right_on = ['User_ID', 'Datetime', 'Text']).drop(['Diff_in_Seconds','diff_abs','same_author','Text_raw'], axis=1)


    #Merge text and timestamps in rows that have the same messageId
    df_questions['Text'] = df_questions.groupby(['messageId'])['Text'].transform(lambda x : ' '.join(x))
    df_questions.dropna(axis=1, how='all', inplace=True)
    df_questions['Timestamp'] = df_questions.groupby(['messageId'])['Timestamp'].transform(lambda x : ','.join(map(str, x)))


    #rename to ids in both dataframes
    df_questions.rename(columns={"Timestamp": "Question_ID", "Text":"Question_Text"}, inplace=True)


    #Drop duplicates
    df_questions = df_questions.drop_duplicates(subset=["Question_Text","Question_ID"],keep='first')



    print('Shape of new questions_df', df_questions.shape)
    
    return df_questions