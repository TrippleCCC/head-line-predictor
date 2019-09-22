# HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
# HHHHHHHHHH - IMPORTANT - HHHHHHHHHHHHHHHHH
# go to command prompt and execute "pip install PySimpleGui27"
# HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH

import random
from collections import defaultdict
import PySimpleGUI27 as gui

class MarkovModel:
    def __init__(self, order):
        self.order = order
        self.chain = {}

    def __str__(self):
        string = ""
        for entry in self.chain:
            tmp = dict(self.chain[entry])
            count = tmp.pop("__count__")
            string += str(entry) + " - " + str(tmp) + " - " + str(count) + "\n"
        return string

    def add_data(self, data):
        sub_chain = markov_chain(data, self.order)
        if len(self.chain) > 0:
            for entry in sub_chain:
                self.merge_probabilities(entry, sub_chain[entry])
        else:
            self.chain = sub_chain

    def merge_probabilities(self, observed, new_probs):
        if observed in self.chain:
            current_probs = self.chain[observed]
        else:
            current_probs = {"__count__":0}
        # Un-normalize current probabilities
        for prob_id in current_probs:
            if prob_id != "__count__":
                current_probs[prob_id] *= current_probs["__count__"]
        # Un-normalize new probabilities
        for prob_id in new_probs:
            if prob_id != "__count__":
                new_probs[prob_id] *= new_probs["__count__"]
        # Add occurences
        for prob_id in new_probs:
            if prob_id != "__count__":
                if prob_id in current_probs:
                    current_probs[prob_id] += new_probs[prob_id]
                else:
                    current_probs[prob_id] = new_probs[prob_id]
                current_probs["__count__"] += new_probs[prob_id]
        # Re-normalize
        for prob_id in current_probs:
            if prob_id != "__count__":
                current_probs[prob_id] /= float(current_probs["__count__"])
        self.chain[observed] = current_probs

    def predict(self, last, num, available_options):
        """
        Predict the next num values given the model and the last values.
        """
        output_list = []
        list_last = list(last)
        while num > 0:
            last_tuple = tuple(list_last)
            if self.chain.has_key(last_tuple) == True: # Look for the key in the dictionary, and if found, redo the probability values
                value_wheights = dict(self.chain[last_tuple])
                value_wheights.pop("__count__")

                rand = random.random()

                wheight_sum = 0

                for value in value_wheights: # Code for a weighted probability choice
                    wheight_sum += value_wheights[value]
                    if wheight_sum > rand:
                        prob_value = value
                        break

            elif self.chain.has_key(last_tuple) == False: # If the key is not found, choose a random option
                prob_value = random.choice(available_options)

            output_list.append(prob_value)
            num -= 1
            list_last.pop(0) # these two lines modify last, so that we advance through the data as we generate it
            list_last.append(prob_value)

        return output_list


def markov_chain(data, order):
    """
    Create a Markov chain with the given order from the
    given list of data.
    """

    tuple_list = [] # This list wil contain all the tuples created from slicing the data list
    for index in range(len(data) - order):
        counter = 0
        list1 = []
        while counter < order:
            list1.append(data[index + counter])
            counter += 1
        tuple1 = tuple(list1)
        tuple_list.append(tuple1)

    data_dictionary = defaultdict(int) # This is the main output dictionary

    for index in range(len(tuple_list)):
        data_dictionary[tuple_list[index]] = defaultdict(int) # Add all the tuples as keys, and more defaultdicts as values
    for index in range(len(tuple_list)):
        data_dictionary[tuple_list[index]][data[index + len(tuple_list[index])]] += 1 # Fill the inner values with the amount of times a certain event happens

    for key in data_dictionary: # This loop converts the inner dictionaries from amount of occurrences to actual probabilities
        total_count = 0
        for item in data_dictionary[key]:
            total_count += data_dictionary[key][item]
        for item in data_dictionary[key]:
            data_dictionary[key][item] = (data_dictionary[key][item] / float(total_count))
        data_dictionary[key]["__count__"] = total_count

    final_dictionary = dict(data_dictionary)
    for i in data_dictionary:
        final_dictionary[i] = dict(data_dictionary[i])

    return final_dictionary

def predict(model, last, num):
    """
    Predict the next num values given the model and the last values.
    """
    output_list = []
    list_last = list(last)

    while num > 0:
        last_tuple = tuple(list_last)

        if model.has_key(last_tuple) == True: # Look for the key in the dictionary, and if found, redo the probability values
            value_wheights = model[last_tuple]

            rand = random.random()

            wheight_sum = 0

            for value in value_wheights: # Code for a weighted probability choice
                wheight_sum += value_wheights[value]
                if wheight_sum > rand:
                    prob_value = value
                    break

        elif model.has_key(last_tuple) == False: # If the key is not found, choose a random option
            prob_value = random.randint(0,3)

        output_list.append(prob_value)
        num -= 1
        list_last.pop(0) # these two lines modify last, so that we advance through the data as we generate it
        list_last.append(prob_value)

    return output_list

def mse(result, expected):
    """
    Calculate the mean squared error between the sequences
    result and expected.
    """
    square_error = 0
    for index in range(len(expected)):
        square_error += (result[index] - expected[index])**2
    mean_square_error = square_error / float(len(expected))

    return mean_square_error

def run_experiment(train, order, test, future, actual, trials):
    """
    Run an experiment to predict the future of the test
    data given the training data.  Returns the average
    mean squared error over the number of trials.

    train  - training data
    order  - order of the markov model to use
    test   - "order" days of testing data
    future - number of days to predict
    actual - actual results for next "future" days
    trials - number of trials to run
    """
    trials_counter = int(trials)
    mse_total = 0
    model = markov_chain(train, order)
    while trials_counter > 0:
        result = predict(model, test, future)
        mse_total += mse(result, actual)
        trials_counter -= 1
    mse_average = mse_total / float(trials)

    return mse_average

def load_data(filename, idx=0, max_amount=float('inf')):
    articles = []
    #with open(filename, encoding="ISO-8859-1") as f:
    with open(filename) as f:
        csv_f = csv.reader(f)
        i = 0
        for row in csv_f:
            articles.append(row[idx])
            i += 1
            if i > max_amount:
                break
    return articles

def get_new_headlines(n, kword=None):
    words = []
    starter_words = []
    order = 2
    model = MarkovModel(order)
    headlines = load_data("million.csv", idx=-1, max_amount=3000)
    headlines.pop(0)
    for line in headlines:
        chunks = line.split(" ")
        if len(chunks) > order:
            starter = []
            for i in range(order):
                starter.append(chunks[i])
            if kword != None:
                if kword.lower() in starter:
                    starter_words.append(starter)
            else:
                starter_words.append(starter)
            for i in chunks:
                if i not in words:
                    words.append(i)
            model.add_data(chunks)
    #print model
    #print starter_words

    generated_headlines = []
    for j in range(n):
        random_word = tuple(random.choice(starter_words))
        #print "Random seed word: " + str(random_word)
        #print model.chain[random_word]
        result = list(random_word) + model.predict(random_word, 30, [""])
        string = ""
        for i in result:
            if i != "":
                string += i.capitalize() + " "
        string = string[:-1]
        generated_headlines.append(string)
    return generated_headlines

if __name__ == '__main__':
    import csv
    """
    output = get_new_headlines(10)
    for i in output:
        print i
    """

    """
    model = MarkovModel(2)
    data_set1 = ["1", "2", "2", "3", "1", "3", "2", "2", "1", "3"]
    data_set2 = ["1", "2", "4"]
    model.add_data(data_set1)
    print model
    model.add_data(data_set2)
    print model
    model.add_data(data_set2)
    print model
    """

    """
    import csv
    words = []
    starter_words = []
    order = 2
    model = MarkovModel(order)
    headlines = load_data("million.csv", idx=-1, max_amount=3000)
    headlines.pop(0)
    for line in headlines:
        chunks = line.split(" ")
        if len(chunks) > order:
            starter = []
            for i in range(order):
                starter.append(chunks[i])
            starter_words.append(starter)
            for i in chunks:
                if i not in words:
                    words.append(i)
            model.add_data(chunks)
    #print model
    #print starter_words

    for j in range(20):
        random_word = tuple(random.choice(starter_words))
        #print "Random seed word: " + str(random_word)
        #print model.chain[random_word]
        result = list(random_word) + model.predict(random_word, 20, [""])
        string = ""
        for i in result:
            if i != "":
                string += i.capitalize() + " "
        string = string[:-1]
        print string
    """

    window_layout = [[gui.Frame("", layout=[[gui.Text("What if the past really defined the future?")],
                                            [gui.Text("Press submit and find out! Keyword optional.")],
                     [gui.InputText(default_text="", size=(54, 1), key="keyword", do_not_clear=True)],
                     [gui.Button("Submit", size=(46, 2))],
                     [gui.Multiline(default_text="", do_not_clear=True, size=(52, 10), key="output")]])]]

    window_title = "News Predictor"
    window = gui.Window(window_title).Layout(window_layout)

    #indow.FindElement("error_box").Update(value=ERROR_MESSAGE, append=True)

    # Window positioning:
    event, values = window.Read(timeout=100)
    window.Move(10, 10)
    # Main program loop: ==========================================================
    while 1 == 1:
        event, values = window.Read(timeout=100)
        if event == "Exit" or event == None:
            break

        if event == "Submit":
            kwrd = values["keyword"]
            if kwrd == "":
                kwrd = None
            news = get_new_headlines(5, kword=kwrd)
            string_output = ""
            for i in news:
                string_output += i + "\n"
            window.FindElement("output").Update(string_output)

