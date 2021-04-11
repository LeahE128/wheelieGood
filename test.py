import pickle

decisionTree = pickle.load(open("decisionTreeModel.pkl", "rb"))
knn = pickle.load(open("knnModel.pkl", "rb"))
randomForest = pickle.load(open("randomForestModel.pkl", "rb"))


prediction = decisionTree.predict([[100, 5, 300, 80, 1, 0, 0, 0, 0, 0, 6, 20]])
print(prediction[0])

prediction = randomForest.predict([[100, 5, 300, 80, 1, 0, 0, 0, 0, 0, 6, 20]])
print(prediction[0])

prediction = knn.predict([[100, 5, 300, 80, 1, 0, 0, 0, 0, 0, 6, 20]])
print(prediction[0])