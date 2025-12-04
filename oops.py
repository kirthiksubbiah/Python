class Car:
    def __init__(self, brand, color, mileage):
        self.brand = brand
        self.color = color
        self.mileage = mileage

    def details(self):
        return f"{self.brand} - {self.color} - {self.mileage} km/l"

car1 = Car("BMW", "Black", 12)
car2 = Car("Audi", "White", 14)

print(car1.details())
print(car2.details())
