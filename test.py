import pickle
stations = [9, 28, 27, 41, 53, 62, 79, 114]


for x in stations:
    for y in range(0, 23):
        randomForest = pickle.load(open(f"pickle_jar/dailyModels/randForest{x}.pkl", "rb"))
        prediction = randomForest.predict([[300, 80, 1, 0, 0, 0, 0, 0, y, 2]])
        print(f"Station {x}: ", prediction)
