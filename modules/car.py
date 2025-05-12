# Datu struktūra priekš projekta

class Car:
    def __init__(self, id, description, url, model, year, engine, mileage, price, retrieved):
        self.id = id
        self.description = description
        self.url = url
        self.model = model
        self.year = year
        self.engine = engine
        self.mileage = mileage
        self.price = price
        self.retrieved = retrieved

    # pārveidot uz dictonary, lai vieglāk saglabāt excel file
    def to_dict(self):
        return {
            'ID': self.id,
            'Description': self.description,
            'URL': self.url,
            'Model': self.model,
            'Year': self.year,
            'Engine': self.engine,
            'Mileage': self.mileage,
            'Price': self.price,
            'Retrieved': self.retrieved
        }
    
class CarWebScraping:
    def __init__(self):
        self.cars = []

    def add(self, car):
        self.cars.append(car)
    
    def to_data(self):
        data = []
        for car in self.cars:
            car_dict = car.to_dict()
            data.append(car_dict)
        
        return data
    
print("car.py loaded")
