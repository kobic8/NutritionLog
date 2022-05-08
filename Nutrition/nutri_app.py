def get_measures_from_user():
    """
    This procedure gets from the user its personal measures and returns it as a dictionary

    Returns
    -------
    measures [dict]: with key-values of: current weight, height, BMR
    """
    measures = dict()
    with st.form("New measures"):
        measures['weight'] = st.text_input("How much you weigh now? [kg]\n")
        measures['height'] = st.text_input("What is your height? [cm]\n")
        measures['BMR'] = st.text_input("What is your BMR? [kcal]\n")
        check_save = st.form_submit_button("Data is correct, please update the dataset")
        if not check_save:
            st.info("Please enter your measures and click to save")
    return measures


def get_date():
    update_date = datetime.now().strftime("%B %d")
    st.text(f"Default date to update is for today: {update_date}")
    change_date = st.checkbox('Click here to change the date')
    if change_date:
        date = st.date_input("Choose a day to view?")
        update_date = date.strftime("%B %d")
        return update_date


def present_day(filename, date):
    import matplotlib.pyplot as plt
    # ASSUME: date exists in xls sheets
    daily_log_df = nut.read_daily_log(filename, date)
    total_calories, last_update = nut.get_total_calories(filename, date)
    st.text(f"last update for {date} was on {last_update}")
    st.text(total_calories)
    # TODO: Think about converting this to a pd dataframe and present it to table?
    total_consumed, total_values = nut.sum_daily_log(filename, date, daily_log_df)
    values = [value/total_consumed*100 for value in total_values.values()]
    fig, ax = plt.subplots()
    headers = [header for header in total_values.keys()]
    # st.text(headers)
    ax.pie(values, labels=headers, autopct='%1.1f%%')
    ax.axis('equal')
    ax.set_title(f' Total of {"{:.2f}".format(total_consumed)} calories consumed for: {date} ')
    st.pyplot(fig)

    # values = [value for value in total_calories.values()]
    # headers = [header for header in total_calories.keys()]
    # st.bar_chart(values, headers)
    chart = st.bar_chart(pd.DataFrame(total_calories, index=['Total']))
    # st.altair_chart(chart)


if __name__ == '__main__':
    import streamlit as st
    import main_nutrition_log as nut
    from os import path
    from datetime import datetime
    import pandas as pd
    from matplotlib import pyplot as plt

    # main page
    st.title("Kobic's Nutrition App")
    filename = 'nutrition_log.xlsx'
    initialized = False
    updated_measures = False
    if not path.isfile(filename):
        measures_input = None
        initialized = nut.init(filename)
        if initialized:
            st.success("nutrition_log.xlsx is created")
            measures_input = get_measures_from_user()
            if measures_input is not None:
                updated_measures = nut.update_worksheet_measures(filename, measures_input)
                if updated_measures:
                    st.success("Dataset is updated")

    st.header("What would you like to do today?")
    action = st.radio("Please choose your action", ("View my day", "Update my day", "Update my measures"))
    if action == "Update my measures":
        measures_input = None
        measures_input = get_measures_from_user()
        if measures_input is not None:
            nut.update_worksheet_measures(filename, measures_input)
            st.success("Dataset is updated")
        st.text(measures_input)
    if action == "View my day":
        save_date = False
        with st.form("Choose date to view"):
            date = get_date()
            save_date = st.form_submit_button(f"Save: {date}")
            # FIXME: what if we choose a date that is not in the xls? we should check and offer
        if save_date:
            # st.text(f"Data for {date} was last updated on: {nut.get_last_update(filename, date)}")
            present_day(filename, date)
        save_date = False

    if action == "Update my day":
        # get date to edit
        save_date = False
        daily_log_df = None
        food_names, food_dict = nut.read_food_dict()
        with st.form("Choose date to view"):
            date = get_date()
            save_date = st.form_submit_button(f"Save: {date}")
        # if save_date:
        startrow = 8
        daily_log_df = nut.read_daily_log(filename, date)
        if daily_log_df is not None:
            startrow += len(daily_log_df)
            total_cal, updated = nut.get_total_calories(filename, date)
            st.info(f"Data for {date} was last updated on: {updated}")
            st.info(f"Total calories consumed so far: {total_cal['consumed']}")
        else:
            st.info(f"No data is updated for {date} so far, hence, new xls sheet is added.")

        done_button = False
        # while done_button is False:
        with st.form("Add Food"):
            save_date = False
            food = False
            amount = False
            food = st.selectbox("What did you eat", food_names)
            if food:
                units = food_dict[food]['Unit']
                amount = st.text_input(f"How much [{units}] did you eat?")
            if amount:
                amount = float(amount)
            st.text(f" the amount is {amount} and type: {type(amount)}")
            save = None
            save = st.form_submit_button("Save")
            if save:
                row_to_add = nut.create_rwo_to_add(food_dict, food, amount)
                update = nut.update_food_log(filename, date, row_to_add, startrow)
                daily_log_df = nut.read_daily_log(filename, date)
                startrow += 1

                st.text(f"row is: {startrow}")
                st.dataframe(daily_log_df)
                if update:
                    st.success("Dataset is updated")
            next_button = st.form_submit_button("Next")
            if next_button:
                food = False
                amount = False
                units = False
                save = False

        done_button = st.checkbox("Done")
        # burned = 0
        if done_button:
            save_date = False
            food = False
            amount = False
            refresh = False
            done_burned_button = False
            update_cal = False
            cal_burned = None
            get_burned = False
            burned = False
            with st.form("Calories burned"):
                # TODO: use update burned as another option
                burned = st.text_input(f"Update total calories burned on {date}")
                if burned:
                    burned = float(burned)
                    st.text(f"get burned is: {burned}")
                refresh = st.form_submit_button('Refresh')
                if refresh:
                    st.text(f"Burned: {burned}")
                    total_consumed, total_values = nut.sum_daily_log(filename, date, daily_log_df)
                    update_cal = nut.update_total_calories(filename, date, total_consumed, burned)
                    if update_cal:
                        st.success("Dataset is updated")

            done_burned_button = st.checkbox("Done updating")
            if done_burned_button:
                present_day(filename, date)
            # st.info("Now the total calories consumed will be summed up and presented")
            # get_burned = st.button(f"Update total calories burned on {date}")
            # if get_burned:
            #     st.text(f"get burned is: {get_burned}")
            #     # st.text(f"Burned: {burned}")
            #     # burned = st.number_input("Total calories burned")
            #     burned = False
            #     burned = st.text_input("Total calories burned")
            #     if burned:
            #         st.text(f" burned is: {burned}")
            #         cal_burned = float(burned)
            #         st.text(f"Burned: {cal_burned}")
            # st.text(f"Burned: {cal_burned}")
            # refresh = st.button('Refresh')
            # if refresh:
            #     st.text(f"Burned: {cal_burned}")
            #     total_consumed, total_values = nut.sum_daily_log(date, daily_log_df)
            #     update_cal = nut.update_total_calories(filename, date, total_consumed, cal_burned)
            #     if update_cal:
            #         present_day(filename, date)
            # refresh = False
            # update_cal = False


