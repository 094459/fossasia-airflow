import csv

def parse_csv_to_list(filepath):

        with open(filepath, newline="\n") as file:
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader, None)
            result_list = []
            for row in csv_reader:
                print(row)  # Print the current row
                result_list.append(row)
            return result_list # Skip the header row
            #return list(csv_reader)

parse_csv_to_list("demo-joke.csv")