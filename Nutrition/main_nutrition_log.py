def init(date):
    from datetime import datetime
    import pandas as pd
    df_date = pd.DataFrame({'last updated:': datetime.now().strftime("%B %d %Y %H:%M")})
    df_cal_summary = pd.DataFrame({'caloric balance': '0', 'total calories consumed': '0', 'total calories burned:': '0'})
    # ASSUME: I don't need to build the header lines, and will put them as I build the log
    dfs = [df_date, df_cal_summary]
    startrow = 0
    with pd.ExcelWriter('try_'+filename) as writer:
        for df in dfs:
            # FIXME does this updates the sheet? or overrides it?
            df.to_excel(writer, sheet_name=date, engine="xlsxwriter", startrow=startrow)
            startrow += (df.shape[0] + 2)


def read_food_dict():
    """
    The procedure reads the nutritional data of the foods and returns list of food names and values
    Returns
    -------
    food_names [list]: list of food names
    food_dict [dict]:  key = food name and value = {Amount, Units, Calories, Protein, Carbs, Fat}
    """
    import pandas as pd
    # ASSUME: the food dictionary exists, what if not? try-except?
    food_df = pd.read_excel('FoodDictionary.xlsx', index_col=None)
    food_list = food_df.to_dict(orient='records')
    food_names = [value['Food'] for value in food_list]
    food_dict = {row.pop('Food'): row for row in food_list}
    return food_names, food_dict


def get_personal_measures():
    """
    This procedure search if the personal measures of the user exists on the xls file and retrieve it.
    In case the xls does not exist or the data, it gets the personal measures from the user.
    Returns
    -------
    personal_measures {} with keys of: height, BMR, weight
    """
    measures = read_personal_measures()
    if measures is None:
        measures = update_personal_measures()
    return measures


def read_personal_measures():
    """
    This procedure reads the personal measures of the user from the xls file, retrieve it as a dataframe and converts
    it to a dictionary.
    Returns
    -------
    df_measures [dict] with values of: height, BMR, weight
    """
    from os import path
    import pandas as pd
    # ASSUME: if xls exists, than it MUST have the personal measures sheet
    if path.isfile(filename):
        df_measures = pd.read_excel(filename, sheet_name='measures', index_col=None)
        print(df_measures.iloc[:, 1:])
        # index is dropped
        # FIXME consider an alternative way for dealing with the index of the pds-df
        return df_measures.iloc[:, 1:].to_dict(orient='records')[0]
    else:
        return None


def update_personal_measures():
    """
    This procedure gets input from the user personal measures and updates the xls file.
    Returns
    -------
    personal_measures [dict] with keys of: height, BMR, weight
    """
    import pandas as pd
    from os import path
    from openpyxl import load_workbook
    measures = dict()
    measures['weight'] = input("How much you weigh now? [kg]\n")
    measures['height'] = input("What is your height? [cm]\n")
    measures['BMR'] = input("What is your BMR? [kcal]\n")
    df_measures = pd.DataFrame([measures])
    if path.isfile(filename):
        writer = pd.ExcelWriter(filename, engine="openpyxl", mode='a')
        writer.book = load_workbook(filename)
        # notes for the case the xls file was locked for some reason
        # writer.book.security.lockStructure = False
        # writer.close()
    else:
        writer = pd.ExcelWriter(filename, engine="xlsxwriter")
    df_measures.to_excel(writer, sheet_name='measures')
    writer.save()
    return measures


if __name__ == '__main__':
    filename = 'nutrition_log.xlsx'
    food_dict, food_name_list = read_food_dict()
    personal_measures = get_personal_measures()
