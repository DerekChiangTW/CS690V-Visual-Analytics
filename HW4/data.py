import re
import pandas as pd
from os.path import dirname, join


def checkNaN(df):
    """ Check if the dataframe contains NaN values. """

    if df.isnull().values.any():
        N = df.isnull().sum().sum()
        print("There are {} missing values in the dataset.".format(N))


def convert_categorical_data(df):
    """ Convert the categorical columns to numerical data type. """

    for col in df.columns:
        if df[col].dtype is pd.np.dtype('object'):
            df[col] = df[col].astype('category')

    cat_columns = df.select_dtypes(['category']).columns
    df[cat_columns] = df[cat_columns].apply(lambda x: x.cat.codes)


def process_data():

    # Read in dataset
    fpath = join(dirname(__file__), 'data/nutrition_raw_anonymized_data.csv')
    df = pd.read_csv(fpath)

    # Check data and transform categorical data to numrical values
    checkNaN(df)
    convert_categorical_data(df)

    # Separate input features into different categories
    pet_features = ['cat', 'dog']
    hand_features = ['left_hand', 'right_hand']

    text = 'smok[e, i]'
    smoke_features = [col for col in df.columns if re.search(text, col)]

    fruits = ['MELON', 'BERR[I, Y]', 'BANANA',
              'APPLE', 'ORANGE', 'PEACH', 'FRUIT']
    text = '|'.join(fruits)
    fruit_features = [col for col in df.columns if re.search(text, col)]

    text = 'FREQ|QUAN'
    food_features = [col for col in df.columns if (
        re.search(text, col)) and (col not in fruit_features)]

    other_features = [col for col in df.columns if col not in pet_features +
                      hand_features + smoke_features + fruit_features + food_features]

    # Create a dict to store all categories
    feature_dict = {
        'Pet': pet_features,
        'Hand': hand_features,
        'Smoke': smoke_features,
        'Fruit': fruit_features,
        'Food': food_features,
        'Others': other_features
    }

    return df, feature_dict
