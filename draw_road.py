import matplotlib.pyplot as plt
import shutil
import os
import imageio as img


# class for graphical purposes (based on one from previous lists)

class SaveRoad:

    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.number_of_images = 0
        self.directory = "Results"
        self.file_names = []

    def show(self):
        plt.figure(self.fig.number)
        plt.show()

    # this method creates a directory for results
    def create_directory(self):
        try:
            shutil.rmtree(self.directory)
        except FileNotFoundError:
            pass
        os.mkdir(self.directory)

    def save(self):
        path = os.path.join(self.directory, 'step_{0:0>4}.png'.format(self.number_of_images))
        self.fig.savefig(path)
        self.number_of_images += 1
        self.file_names.append(path)

    def gif(self, fps=2):
        images = []
        path = os.path.join(self.directory, 'simulation.gif')
        for file_name in self.file_names:
            images.append(img.imread(file_name))
        img.mimsave(path, images, fps=fps)
