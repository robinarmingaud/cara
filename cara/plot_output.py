from dataclasses import field
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import pandas as pd
import csv

import cara.monte_carlo as mc
from cara import models
from cara.monte_carlo.data import activity_distributions
from tqdm import tqdm
from scipy.spatial import ConvexHull

def get_enclosure_points(x_coordinates, y_coordinates):
    df = pd.DataFrame({'x': x_coordinates, 'y': y_coordinates})

    points = df[['x', 'y']].values
    # get convex hull
    hull = ConvexHull(points)
    # get x and y coordinates
    # repeat last point to close the polygon
    x_hull = np.append(points[hull.vertices,0],
                        points[hull.vertices,0][0])
    y_hull = np.append(points[hull.vertices,1],
                        points[hull.vertices,1][0])
    return x_hull, y_hull

SAMPLE_SIZE = 50000

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

points = 600
viral_loads = np.linspace(2, 12, points)

er_means = []
er_medians = []
lower_percentiles = []
upper_percentiles = []

for vl in tqdm(viral_loads):
    exposure_mc = mc.ExposureModel(
        concentration_model=mc.ConcentrationModel(
            room=models.Room(volume=100, humidity=0.5),
            ventilation=models.AirChange(
                active=models.SpecificInterval(((0, 24),)),
                air_exch=0.25,
            ),
            infected=mc.InfectedPopulation(
                number=1,
                virus=models.Virus(
                    viral_load_in_sputum=10**vl,
                    infectious_dose=50.,
                ),
                presence=mc.SpecificInterval(((0, 2),)),
                mask=models.Mask.types["No mask"],
                activity=activity_distributions['Seated'],
                expiration=models.MultipleExpiration(
                    expirations=(models.Expiration.types['Talking'],
                                 models.Expiration.types['Breathing']),
                    weights=(0.3, 0.7)),
            ),
        ),
        exposed=mc.Population(
            number=14,
            presence=mc.SpecificInterval(((0, 2),)),
            activity=models.Activity.types['Seated'],
            mask=models.Mask.types["No mask"],
        ),
    )
    exposure_model = exposure_mc.build_model(size=SAMPLE_SIZE)
    emission_rate = exposure_model.concentration_model.infected.emission_rate_when_present()
    er_means.append(np.mean(emission_rate))
    er_medians.append(np.median(emission_rate))
    lower_percentiles.append(np.quantile(emission_rate, 0.01))
    upper_percentiles.append(np.quantile(emission_rate, 0.99))

with open('data.csv', 'w', newline='') as csvfile:
    fieldnames = ['viral load', 'emission rate']
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    thewriter.writeheader()
    for i, vl in enumerate(viral_loads):
        thewriter.writerow(
            {'viral load': 10**vl, 'emission rate': er_means[i]})

ax.plot(viral_loads, er_means)
ax.fill_between(viral_loads, lower_percentiles,
                upper_percentiles, alpha=0.2)
ax.set_yscale('log')

############# Coleman #############
coleman_etal_vl = [np.log10(821065925.4), np.log10(1382131207), np.log10(81801735.96), np.log10(487760677.4), np.log10(2326593535), np.log10(1488879159), np.log10(884480386.5)]
coleman_etal_er = [127, 455.2, 281.8, 884.2, 448.4, 1100.6, 621]
plt.scatter(coleman_etal_vl, coleman_etal_er)
x_hull, y_hull = get_enclosure_points(coleman_etal_vl, coleman_etal_er)
# plot shape
plt.fill(x_hull, y_hull, '--', c='orange', alpha=0.2)

############# Markers #############
markers = ['*', 'v', 's']

############# Milton et al #############
milton_vl = [np.log10(8.30E+04), np.log10(4.20E+05), np.log10(1.80E+06)]
milton_er = [22, 220, 1120] # removed first and last due to its dimensions
for i, point in enumerate(milton_vl):
    plt.scatter(point, milton_er[i], marker=markers[i], color='red')
x_hull, y_hull = get_enclosure_points(milton_vl, milton_er)
# plot shape
plt.fill(x_hull, y_hull, '--', c='red', alpha=0.2)

############# Yan et al #############
yan_vl = [np.log10(7.86E+07), np.log10(2.23E+09), np.log10(1.51E+10)] # removed first and last due to its dimensions
yan_er = [8396.78166, 45324.55964, 400054.0827]
for i, point in enumerate(yan_vl):
    plt.scatter(point, yan_er[i], marker=markers[i], color='green')
x_hull, y_hull = get_enclosure_points(yan_vl, yan_er)
# plot shape
plt.fill(x_hull, y_hull, '--', c='green', alpha=0.2)

# Milton
boxes = [
    {
        'label': "Milton data",
        'whislo': 0,    # Bottom whisker position
        'q1': 22,    # First quartile (25th percentile)
        'med': 220,    # Median         (50th percentile)
        'q3': 1120,    # Third quartile (75th percentile)
        'whishi': 260000,    # Top whisker position
        'fliers': []        # Outliers
    }
]
# `box plot aligned with the viral load value of 5.62325
ax.bxp(boxes, showfliers=False, positions=[5.62324929])

# Yan

boxes = [
    {
        'whislo': 1424.81,    # Bottom whisker position
        'q1': 8396.78,    # First quartile (25th percentile)
        'med': 45324.6,    # Median         (50th percentile)
        'q3': 400054,    # Third quartile (75th percentile)
        'whishi': 88616200,    # Top whisker position
        'fliers': []        # Outliers
    }
]
ax.bxp(boxes, showfliers=False, positions=[9.34786])

# box plot aligned with the viral load value of 9.34786

############ Legend ############
min = mlines.Line2D([], [], color='gray', marker='_', linestyle='None', label = 'Min')
first_quantile = mlines.Line2D([], [], color='gray', marker='*', linestyle='None', label = '25th quantile')
second_quantile = mlines.Line2D([], [], color='gray', marker='v', linestyle='None', label = 'Mean')
third_quantile = mlines.Line2D([], [], color='gray', marker='s', linestyle='None', label = '75th quantile')
max = mlines.Line2D([], [], color='gray', marker='+', linestyle='None', label = 'Max')
plt.legend(handles=[min, first_quantile, second_quantile, third_quantile, max])

############ Plot ############
plt.title('Exhaled virions while breathing for 1h', fontsize=14)
plt.ylabel('RNA copies', fontsize=12)
plt.xticks(ticks=[i for i in range(2, 13)], labels=[
    '$10^{' + str(i) + '}$' for i in range(2, 13)])
plt.xlabel('NP viral load (RNA copies mL$^{-1}$)', fontsize=12)
plt.show()