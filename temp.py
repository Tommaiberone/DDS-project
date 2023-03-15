import numpy as np

# arr = np.random.randint(low=0, high=9, size=200)

# print(arr)

with open('values.txt', 'r') as file:
			values = file.read()
			values = values.split(" ")
			print(values)
			print(len(values))