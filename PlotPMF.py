import scipy.ndimage
import matplotlib.pyplot as plt
from matplotlib import cm
import scipy.ndimage
import numpy as np

def plot_pmf_image(molecule, title, data) -> plt.Figure:
    """Method to create a Ramachandram plot"""
    x, y, z = [], [], []

    xline, yline, zline = [], [], []

    for line in data:
        if len(line) >= 3:
            nextX = line[0]
            if xline and (xline[-1] != nextX):  # End of row
                x.append(xline)
                y.append(yline)
                z.append(zline)
                xline, yline, zline = [], [], []

            nextY = line[1]
            nextZ = line[2]

            xline.append(nextX)
            yline.append(nextY)
            zline.append(nextZ)

    # Append the last row
    if xline:
        x.append(xline)
        y.append(yline)
        z.append(zline)

    # Convert lists to numpy arrays for processing
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    # Smoothing data
    z = scipy.ndimage.gaussian_filter(z, sigma=1)  # Adjust sigma for more or less smoothing

    # Create the plot
    fig = plt.figure(figsize=(6, 6))  # Set figure size to be square
    a = fig.add_subplot(1, 1, 1)

    levs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Levels to draw contours at
    CS = a.contour(x, y, z, levs, cmap=cm.coolwarm)

    # Define a class that formats float representation
    class nf(float):
        def __repr__(self):
            str_val = '%.1f' % (self.__float__(),)
            if str_val[-1] == '0':
                return '%.0f' % self.__float__()
            else:
                return '%.1f' % self.__float__()

    # Recast levels to new class
    CS.levels = [nf(val) for val in CS.levels]

    # Label levels with specially formatted floats
    plt.clabel(CS, CS.levels, inline=True, fmt='%r ', fontsize=8)

    # Remove axis labels and ticks
    a.set_xticks([])
    a.set_yticks([])
    a.set_xlabel('')
    a.set_ylabel('')

    # Set aspect ratio to be equal and remove margins
    a.set_aspect('equal', adjustable='box')
    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)


    return fig

