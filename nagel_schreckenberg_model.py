from typing import Optional, List
import numpy as np
import matplotlib.pyplot as plt
from draw_road import SaveRoad
import matplotlib.colors as clrs


# class Car produces car object with velocity and color
class Car:
    def __init__(self, number, hue):
        self.velocity = 0
        self.number = number
        self.hue = hue  # color: hue in HSV color format (different color for every car)

    def __repr__(self):
        return 'Car ' + str(self.number)


# implementation of Nagel-Schreckenberg Model
class NagelSchreckenbergModel:
    road: List[Optional[Car]]  # declaring expected type of road (to surpass warning message)

    def __init__(self, L, car_density, max_velocity, slowing_probability, save_graphics=False):
        self.L = L
        self.car_density = car_density
        self.max_velocity = max_velocity
        self.slowing_probability = slowing_probability
        self.number_of_cars = int(
            round(L * car_density))  # produces number of cars for given road size (L) and car density
        self.road = [None] * L  # we are implementing road as a list; None - empty cell, object from Car class - car
        self.average_velocities = []
        initial_car_indices = sorted(
            np.random.choice(L, self.number_of_cars, replace=False))  # random placement of cars on the road
        for i in range(len(initial_car_indices)):
            this_car = Car(i + 1, i / self.number_of_cars)
            self.road[initial_car_indices[i]] = this_car
        self.save_graphics = save_graphics  # flag for graphical purposes
        if save_graphics:
            self.drawing_machine = SaveRoad()
            self.drawing_machine.create_directory()

    def get_velocities(self):  # get a list of car velocities (None if the cell is empty)
        velocities = [None] * len(self.road)
        for i in range(len(self.road)):
            if self.road[i]:
                velocities[i] = self.road[i].velocity
        return velocities

    def simulation(self, number_of_iterations):  # main simulation method
        self.average_velocities = [self.average_velocity()]
        for i in range(number_of_iterations):
            self.acceleration()
            self.slowing()
            self.randomization()
            self.motion()
            self.average_velocities.append(self.average_velocity())
            if self.save_graphics:
                self.draw_road(r_big=4.5, r_small=4, t=i)
                plt.cla()
        if self.save_graphics:
            self.drawing_machine.gif(fps=10)

    def acceleration(self):  # first action of the model
        for cell in self.road:
            if cell:
                cell.velocity = min(cell.velocity + 1, self.max_velocity)

    def slowing(self):  # second
        for i in range(len(self.road)):
            if self.road[i]:
                distance = 0
                while not self.road[(i + distance + 1) % len(self.road)]:  # periodic BCs
                    distance += 1
                self.road[i].velocity = min(self.road[i].velocity, distance)

    def randomization(self):  # third
        for i in range(len(self.road)):
            if self.road[i]:
                if np.random.random() < self.slowing_probability:
                    self.road[i].velocity = max(self.road[i].velocity - 1, 0)

    def motion(self):  # fourth
        new_road = [None] * len(self.road)
        for i in range(len(self.road)):
            if self.road[i]:
                new_road[(i + self.road[i].velocity) % len(self.road)] = self.road[i]  # periodic BCs
        self.road = new_road

    def average_velocity(self):  # calculating average velocity for a time step
        return sum(filter(None, self.get_velocities())) / self.number_of_cars

    def draw_road(self, r_big, r_small, t):  # visualization method
        r_diff = r_small * np.sin(np.pi / self.L) / (1 - np.sin(np.pi / self.L))
        big_circle = plt.Circle((0, 0), r_big, color='darkgray')
        small_circle = plt.Circle((0, 0), r_small, color='w')
        self.drawing_machine.ax.add_artist(big_circle)
        self.drawing_machine.ax.add_artist(small_circle)
        plt.xlim(-(r_big + 2), (r_big + 2))
        plt.ylim(-(r_big + 2), (r_big + 2))
        r_middle = (r_big + r_small) / 2
        theta = np.linspace(0, 2 * np.pi, self.L + 1)
        for i in range(self.L):
            if self.road[i]:
                x = r_middle * np.cos(theta[i])
                y = r_middle * np.sin(theta[i])
                color = clrs.hsv_to_rgb((self.road[i].hue, 1, 1))
                car_circle = plt.Circle((x, y), 0.9 * r_diff, color=color)
                self.drawing_machine.ax.add_artist(car_circle)
        self.drawing_machine.ax.get_xaxis().set_ticks([])
        self.drawing_machine.ax.get_yaxis().set_ticks([])
        self.drawing_machine.ax.set_title('Nagel-Schreckenberg Model, L={0}, no.iter={1}'.format(self.L, t))
        self.drawing_machine.ax.set_xlabel('car density={0}, max velocity={1}, slowing prob.={2}'.format(
            self.car_density,
            self.max_velocity,
            self.slowing_probability))
        self.drawing_machine.save()


if __name__ == '__main__':

    # plot (avg velocity with respect to car density)
    L = 100
    n_iterations = 100
    v_max = 5
    slowing_p_list = [0.2, 0.5, 0.7]
    rho_list = np.linspace(0.1, 0.9, 17)
    for p in slowing_p_list:
        average_velocities_list = []
        for rho in rho_list:
            NSM = NagelSchreckenbergModel(L, rho, v_max, p, save_graphics=False)
            NSM.simulation(n_iterations)
            average_velocities_list.append(sum(NSM.average_velocities) / len(NSM.average_velocities))
        plt.plot(rho_list, average_velocities_list, label='p={0}'.format(p))
    plt.title('Average velocity, L={0}, max velocity={1}, #iter={2}'.format(L, v_max, n_iterations))
    plt.xlabel('car density')
    plt.ylabel('average velocity')
    plt.legend()
    plt.show()

    # gif (example)
    L = 100
    n_iterations = 100
    v_max = 5
    slowing_p = 0.2
    rho = 0.6
    NSM = NagelSchreckenbergModel(L, rho, v_max, slowing_p, save_graphics=True)
    NSM.simulation(n_iterations)
