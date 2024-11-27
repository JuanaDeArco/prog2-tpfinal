import pandas as pd

class DataFrameIterator:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = pd.read_csv(filepath)
        self.df = self.df.fillna(0)
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.df):
            row = self.df.iloc[self.index]
            self.index += 1
            return row
        else:
            raise StopIteration
