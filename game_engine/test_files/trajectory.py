''' projectile_motion.py
projectile motion equations:
height = y(t) = hs + (t * v * sin(a)) - (g * t*t)/2
distance = x(t) = v * cos(a) * t
where:
t is the time in seconds
v is the muzzle velocity of the projectile (meters/second)
a is the firing angle with repsect to ground (radians)
hs is starting height with respect to ground (meters)
g is the gravitational pull (meters/second_square)

tested with Python27/Python33  by  vegaseat  20mar2013
'''

import math
import matplotlib.pyplot as plt


def projectile_xy(speed, angle, starting_height=0.0, gravity=9.8):
    '''
    returns a list of (x, y) projectile motion data points
    where:
    x axis is distance (or range) in meters
    y axis is height in meters
    '''
    data_xy = []
    t = 0.0
    while True:
        # now calculate the height y
        y = starting_height + (t * speed * math.sin(angle)) - (gravity * t * t)/2
        # projectile has hit ground level
        if y < 0:
            break
        # calculate the distance x
        x = speed * math.cos(angle) * t
        # append the (x, y) tuple to the list
        data_xy.append((x, y))
        # use the time in increments of 0.1 seconds
        t += 0.1
    return data_xy

# use a firing angle of 45 degrees
d = 80
a = math.radians(d)  # radians
# muzzle velocity of the projectile (meters/second)
v = 200
data_45 = projectile_xy(v, a)
print "\nDATA: ", data_45, "\n"

# find maximum height ...
point_height_max = max(data_45, key=lambda q: q[1])
xm, ym = point_height_max
print('''
    Projectile Motion ...
Using a firing angle of {} degrees
and a muzzle velocity of {} meters/second
the maximum height is {:0.1f} meters
at a distance of {:0.1f} meters,'''.format(d, v, ym, xm))

# find maximum distance ...
x_max = max(data_45)[0]
print("the maximum distance is {:0.1f} meters.".format(x_max))

''' result ...
    Projectile Motion ...
Using a firing angle of 45 degrees
and a muzzle velocity of 100 meters/second
the maximum height is 255.1 meters
at a distance of 509.1 meters,
the maximum distance is 1018.2 meters.
'''

x = [row[0] for row in data_45]
y = [row[1] for row in data_45]
plt.plot(x, y)
plt.axis([0, 2000, 0, 1500])
plt.xlabel('distance')
plt.ylabel('altitude')

plt.savefig('trajectory.png')
