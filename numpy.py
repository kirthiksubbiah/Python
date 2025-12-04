import numpy as np
arr = np.arange(1, 51)
print(arr)

reshaped = arr.reshape(5, 10)
print(reshaped)

third_col = reshaped[:,2]
print(third_col)

total_sum = reshaped.sum()

mean_value = reshaped.mean()

print(total_sum, mean_value)

A = np.random.randint(1, 10, (3, 3))
B = np.random.randint(1, 10, (3, 3))

print(A)
print(B)

matrix_mul = np.dot(A, B)
print(matrix_mul)
