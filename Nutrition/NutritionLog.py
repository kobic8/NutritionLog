class Food:
    @staticmethod
    def get_food_dictionary():
        import csv
        # Read the CSV file
        filename = 'FoodDictionary.csv'
        with open(filename) as f:
            # Get the headers
            reader = csv.reader(f)
            header_row = next(reader)
            # Create a food dictionary
            food_dict = {}
            for row in reader:
                entry = {}
                # build a dictionary of properties and values for each meal
                for ind in range(1, len(row)):
                    entry[header_row[ind]] = row[ind]
                food_dict[row[0]] = entry
            return food_dict

    @staticmethod
    def get_daily_meals():
        daily_meals = {}
        food_list = list(Food.get_food_dictionary().keys())
        user_input = input("Please enter your meal my name (fully \ partially)\n")
        while not user_input == '0':
            matches = Food.food_lookup(food_list, user_input)
            while len(matches) > 1:
                print("The possible options are: {}".format(matches))
                # TODO enumerate the possible meals and let the user number
                user_input = input("Please refine your choice of meal\n")
                matches = Food.food_lookup(food_list, user_input)
            # Get the amount of food
            meal = matches[0]
            amount = input("How many {} of {} did you eat today fatty?".format(Food.get_food_dictionary()[meal]['Units']
                                                                               , meal))
            # TODO write a try-except for non-numeric values for amount
            calculated_entry = Food.calculate_daily_values(Food.get_food_dictionary()[meal], float(amount))
            daily_meals[meal] = calculated_entry
            user_input = input("Did you eat more today, fatty? hit 0 when you're done\n")
            # TODO check for duplicates in for input from user in meal name, and add
        return daily_meals

    @staticmethod
    def food_lookup(food_list, user_input):
        matches = []
        for meal in food_list:
            if Food.find_match(meal.lower(), user_input.lower()):
                matches.append(meal)
        return matches

    @staticmethod
    def find_match(txt, pattern):
        """ bruteforce search for a pattern in a given string"""
        len_pat = len(pattern)
        ind = 0
        for ch in txt[:]:
            if ch != pattern[ind]:
                ind = 0
            else:
                if ind == len_pat-1:  # The whole pattern is found in the text
                    return True
                else:
                    ind += 1
        return False

    @staticmethod
    def calculate_daily_values(food_entry, amount):
        """ get a meal entry as dict, and an amount of the meal consumed, return updated values"""
        factor = amount / float(food_entry['Amount'])
        for prop in list(food_entry.keys())[-4:]:
            food_entry[prop] = str(factor*float(food_entry[prop]))
        food_entry['Amount'] = str(amount)
        return food_entry

    @staticmethod
    def output_daily_log(daily_meals, plotter):
        from matplotlib import pyplot as plt
        bmr = 2300
        total_val = {}
        for _, nut_prop in daily_meals.items():
            for prop in list(nut_prop.keys())[-4:]:
                # print("prop is {} and value is {}".format(prop, nut_prop))
                if prop in total_val:
                    total_val[prop] = float(total_val[prop]) + float(nut_prop[prop])
                else:
                    total_val[prop] = nut_prop[prop]
        # print("The calorie balance is: {}kCal".format(total_val['Calories']-bmr))
        if plotter:
            # Create pie-chart of values
            fig = plt.figure(figsize=(10, 7))
            plt.pie(list(total_val.values())[1:], labels=list(total_val.keys())[1:])
            plt.show()
        return total_val


class User(Food):
    def __init__(self):
        self.name = input("Welcome to Kobi's fitness, Please enter your name.")
        self.weight = 75
        self.BMR = 2500
        self.data = {}
        print(Food.get_food_dictionary().keys())

    def daily_input(self):
        from datetime import datetime
        date_entry = input("Enter the date in the following CSV format: dd,mm,yy")
        while not date_entry == '0':
            current_date = datetime.strptime(date_entry, "%d,%m,%y")
            # TODO validation tests for checking future date, or wrong date template
            daily_entry = {}
            cal_burned = input("How much calories have you burned today?")
            daily_entry['Burned'] = int(cal_burned)
            daily_meals = Food.get_daily_meals()
            daily_total = Food.output_daily_log(daily_meals, 0)
            # TODO add an option to plot analyze for specific date
            daily_entry['Meals'] = daily_meals
            daily_entry['Consumed'] = float(daily_total['Calories'])
            daily_entry['Balance'] = daily_entry['Consumed'] - daily_entry['Burned']
            self.data[current_date] = daily_entry
            date_entry = input("Enter another date in the following CSV format: dd,mm,yyyy, 0 otherwise")

    def post_process(self):
        import matplotlib.pyplot as plt
        for date, daily_dict in self.data.items():
            print("for the date: {} the balance was: {} kCal".format(date.strftime("%d/%m/%y"), daily_dict['Balance']))
        # plot a graph of: input calories, calories balance VS. date
        # x-axis as dates (keys of the data dict)
        dates = list(map(str, self.data.keys()))
        # inner keys (of values of the dict)
        labels = ['Balance', 'Consumed']
        for label in labels:
            # list of values for inner label
            y_values = [value[label] for value in self.data.values()]
            # plot each inner label
            plt.plot(dates, y_values, label=label)
            # TODO fix the label to have only the date and not the hours/min/sec datum
        plt.legend()
        plt.show()


def main():
    food = Food()
    food_dict = food.get_food_dictionary()
    print(food_dict.keys())

    u1 = User()
    u1.daily_input()
    u1.post_process()
    # TODO save and load user input data by user name (dict?) and their data


if __name__ == '__main__':
    main()
