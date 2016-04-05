import concurrent

class CarRerouter():

  def __init__(self):
    pass

  def reroute_cars(cars):

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(CarRerouter.report, cars)

  def report_cars(cars):

    with concurrent.futures.ProcessPoolExecutor() as executor:
      executor.map(CarRerouter.reroute, cars)

  def reroute(car):

    car.reroute()

  def report(car):

    car.send_reports()