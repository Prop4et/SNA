import pandas as pd

def main():
    df = pd.read_csv('Europrova.csv', dtype=str)
    print(df)

if __name__ == '__main__':
    main()