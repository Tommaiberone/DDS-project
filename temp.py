import numpy as np

# arr = np.random.randint(low=0, high=9, size=200)

# print(arr)

with open('Inputs/values_fast.txt', 'r') as file:
	
	line = file.read()

	values = line.replace("\n", "").split(" ")

	for value in values:
		float_value = float(value)
		float_value *= 25
		print(float_value, end= ' ')

