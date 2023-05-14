Python Robotics Simulator
================================

This is a simple, portable robot simulator developed by [Student Robotics](https://studentrobotics.org).
Some of the arenas and the exercises have been modified for the Research Track I course

Installing and running
----------------------

The simulator requires a Python 2.7 installation, the [pygame](http://pygame.org/) library, [PyPyBox2D](https://pypi.python.org/pypi/pypybox2d/2.1-r331), and [PyYAML](https://pypi.python.org/pypi/PyYAML/).

Once the dependencies are installed, simply run the `test.py` script to test out the simulator.


Robot API
---------

The API for controlling a simulated robot is designed to be as similar as possible to the [SR API][sr-api].

### Motors ###

The simulated robot has two motors configured for skid steering, connected to a two-output [Motor Board](https://studentrobotics.org/docs/kit/motor_board). The left motor is connected to output `0` and the right motor to output `1`.

The Motor Board API is identical to [that of the SR API](https://studentrobotics.org/docs/programming/sr/motors/), except that motor boards cannot be addressed by serial number. So, to turn on the spot at one quarter of full power, one might write the following:

```python
R.motors[0].m0.power = 25
R.motors[0].m1.power = -25
```

### The Grabber ###

The robot is equipped with a grabber, capable of picking up a token which is in front of the robot and within 0.4 metres of the robot's centre. To pick up a token, call the `R.grab` method:

```python
success = R.grab()
```

The `R.grab` function returns `True` if a token was successfully picked up, or `False` otherwise. If the robot is already holding a token, it will throw an `AlreadyHoldingSomethingException`.

To drop the token, call the `R.release` method.

Cable-tie flails are not implemented.

### Vision ###

To help the robot find tokens and navigate, each token has markers stuck to it, as does each wall. The `R.see` method returns a list of all the markers the robot can see, as `Marker` objects. The robot can only see markers which it is facing towards.

Each `Marker` object has the following attributes:

* `info`: a `MarkerInfo` object describing the marker itself. Has the following attributes:
  * `code`: the numeric code of the marker.
  * `marker_type`: the type of object the marker is attached to (either `MARKER_TOKEN_GOLD`, `MARKER_TOKEN_SILVER` or `MARKER_ARENA`).
  * `offset`: offset of the numeric code of the marker from the lowest numbered marker of its type. For example, token number 3 has the code 43, but offset 3.
  * `size`: the size that the marker would be in the real game, for compatibility with the SR API.
* `centre`: the location of the marker in polar coordinates, as a `PolarCoord` object. Has the following attributes:
  * `length`: the distance from the centre of the robot to the object (in metres).
  * `rot_y`: rotation about the Y axis in degrees.
* `dist`: an alias for `centre.length`
* `res`: the value of the `res` parameter of `R.see`, for compatibility with the SR API.
* `rot_y`: an alias for `centre.rot_y`
* `timestamp`: the time at which the marker was seen (when `R.see` was called).

For example, the following code lists all of the markers the robot can see:

```python
markers = R.see()
print "I can see", len(markers), "markers:"

for m in markers:
    if m.info.marker_type in (MARKER_TOKEN_GOLD, MARKER_TOKEN_SILVER):
        print " - Token {0} is {1} metres away".format( m.info.offset, m.dist )
    elif m.info.marker_type == MARKER_ARENA:
        print " - Arena marker {0} is {1} metres away".format( m.info.offset, m.dist )
```

[sr-api]: https://studentrobotics.org/docs/programming/sr/
## Running the assignment: ##
-----------------------------
To run the assignment script in the simulator, use `run.py`, passing it the file names assignment1.py. 

```
$ python run.py assignment1.py
```

## algorithm description: ##
-----------------------------

the assignment1.py file is composed by 4 main methods used to accomplish the requested task, which is to couple all the golden tokens with the silver ones; moreover the hipothesis of avoiding the token during the motion and avoid to move a token already coupled were introduced. 
let we see these methods in detail:
* drive(speed, seconds): this method is used to move the robot straight forward, it's arguments are the speed of the motors (expressed in meters/seconds) and the duration of the motion in seconds rappresented by the argument seconds.
  This function set the power of the two motors to the value specified by speed for a time interval specified by seconds, after that it set the speed to zero again.
```
  def drive(speed, seconds):
      """
      Function for setting a linear velocity
      Args: speed (int): the speed of the wheels
	    seconds (int): the time interval
      """
      R.motors[0].m0.power = speed
      R.motors[0].m1.power = speed
      time.sleep(seconds)
      R.motors[0].m0.power = 0
      R.motors[0].m1.power = 0 
```
* turn(speed, seconds): this method is used to turn the robot in place by assigning an opposite speed to the two motors, it's arguments are the speed of the motors (expressed in meters/seconds) and the duration of the motion in seconds rappresented by the argument seconds.
This function set the power of the two motors to the value specified by speed fot the right motor and to -speed for the left motor, for a time interval specified by seconds, after that it set the speeds to zero again.
```
  def turn(speed, seconds):
      """
      Function for setting an angular velocity
            Args: speed (int): the speed of the wheels 
  	    seconds (int): the time interval
      """
      R.motors[0].m0.power = speed
      R.motors[0].m1.power = -speed
      time.sleep(seconds)
      R.motors[0].m0.power = 0
      R.motors[0].m1.power = 0
```
* find_alone_token(tokenTx, t): this method simulate a computer vision algorithm with the aim of searching for the closer token of type tokenTx, in the robot view, not coupled, meaning with any possible token of different type farther than t [m], for wich the reaching action will not leads to hit any possible token of type different from tokenTx.
in details the arguments of the method are tokenTx, the token type we're searching for, and t, which is the minimum relative distance between a token of type tokenTx and a token of different type under which the two are considered coupled.
the main idea behind this method is:
1. look for all possible tokens of type tokenTx, and put their polar coordinates in the array S_x.
2. look for all possible tokens of type different from tokenTx, and put their polar coordinates in the array S_y.
3. for all the token of type tokenTx evaluate the minimum distance between the token and any other token of type different from tokenTx D and the projection of any of these token on the normal to the line connecting the robot and the desired token Tg.
4. if D is under the threshold t and/or Tg is less then half the track gouge of the robot, and the token of type tokenTx is farther then the one of other type (its width, meaning that a straight motion to the token would imply a collision) discard such token of type tokenTx.
5. among the token left search for the closer to the robot and return its polar coordinates.
6. if no token remain over this selection process the method will return a distance dist and orientation rot_y equal to 1000.

```
  def find_alone_token(tokenTx, t):
    """
    this function simulate a computer vision algorithm, it first localize all the token thank to the method R.see(), it divide them between the token of type tokenTx and the others (the golden and the silver ones)
    between them the algorithm discard the tokens that are already coupled, meaning near to a token of different type at a distance lower then t, and the one for wich the straight path from
    the robot position and the token implies hitting a token of type different from tokenTx
    Args: tokenTx (string): type of token to search for
     t(float): distance under which the tokens are considered as coupled
    """

    S_x=[]
    S_y=[]
    dist = 100 # threshold for the token distance, over that threshold there is no token

    for token in R.see(): #for all the token you can see (in the 180 grad circular sector in front of the robot)
        if token.dist < dist and token.info.marker_type == tokenTx: # put the token of type tokenTx in the array S_x
            S_x.append([token.dist , token.rot_y])
            
        elif token.dist < dist and token.info.marker_type != tokenTx and token.dist > t: # the one of different type in the array S_y
            S_y.append([token.dist , token.rot_y])
    
    for i in range(len(S_x)): # for all the token of type tokenTx evaluate the distance to all the token of different type (checking if they are coupled) and check if the straight trajectory to reach them implies hitting a token different from tokenTx
        a = 0 # reset the flag for both the bad condition
        for j in range(len(S_y)): 
            try:
                D = math.sqrt((((S_x[i][0] * math.cos(round(S_x[i][1], 3) * (math.pi / 180))) - (S_y[j][0] * math.cos(round(S_y[j][1], 3) * (math.pi / 180)))) ** 2) + (((S_x[i][0] * math.sin(round(S_x[i][1], 3) * (math.pi / 180))) - (S_y[j][0] * math.sin(round(S_y[j][1], 3) * (math.pi / 180)))) ** 2)) # distance between the token of type Tx that i want to reach and any token of the opposite type
            except:
                D = 1000
            
            try:
                Tg = S_y[j][0] * math.sin((S_y[j][1] - S_x[i][1]) * (math.pi / 180)) # projection of the token of type different from tokenTx that i don't want to hit, on the normal respect the direction to the token Tx ( so if it's less then half the track gouge it would be hitted)
            except:
                Tg = 10
            
            if D <= t or (abs(Tg) < 0.4 and S_y[j][0] < S_x[i][0]) : # in both the cases...
            	a = 1
        if a == 1:
            S_x.pop(i) # remove it from the list
                           
    try: # among the token that remain search the closest
        """the try - except function is used to handle the case when there is no golden token in the circular sector"""     
        S_min = min(S_x , key=lambda x: x[0]) 
    except:
        S_min=[1000, 1000]

    dist = S_min[0]
    rot_y = S_min[1]
    
    return dist, rot_y # return distance and orientation of it

```
* Move_to_token(tokenTx, d_th): this method move the robot to a position closer then d_th to the token of type tokenTx returned by the previous method, so its arguments are the desired token type tokenTx and the minimum distance d_th to label the reaching action as completed.
the basic idea is to search for the token with the method find_alone_token(), then if the robot is already closer then d_th and oriented under the threshold specified by a_th the action can be concluded since the robot is already in position;
otherwise if the orientation condition is meet, but not the distance one, more forward to get closer to the token and so under the threshold;
else if the the orientation condition is not meet steer the robot in one direction or the other to meet the ondition;
finally if the method returned a distance and orientation equal to 1000 for both, then turn around to search for other tokens.

```
  def Move_to_token(tokenTx, d_th):
    """ this method uses the robot methods drive(),turn() and find_alone_token() methods specified above to find a token of type tokenTx and reach it in a condition that allows to grab it"""
    while 1:
        dist, rot_y = find_alone_token(tokenTx, 0.9)
        if dist < d_th and -a_th <= rot_y <= a_th :
            """in this case i'm in conditions to grab the tokenTx""" 
            print("Reached")
            break
        elif -a_th <= rot_y <= a_th:  
            """ in this case we're alligned with the token and we've just to reach it"""
            print("straight in front of me")
            drive(10, 0.5)
        elif -90 < rot_y < -a_th:
            """ in this case to allign with the token we've to turn left a bit"""
            print("left a bit...")
            turn(-3, 0.5)
        elif 90 > rot_y > a_th:
            """ in this case to allign with the token we've to turn right a bit"""
            print("right a bit...")
            turn(3, 0.5)
        elif dist >= 1000 or rot_y >= 1000 :
            turn(10, 0.5) # no token remained in the list turn around to find one
            print("lost the token")
```

* main(): the main function use the above explained method to achive our task, in particular it first search for a silver token and move the robot to it, it grasp the token and then search for a gold one. once the golden token is reached it release the silver token and search for another one.
this process is iterated till all the avaiable token are coupled.
```
def main():
    tokenTx = MARKER_TOKEN_SILVER
    """string: the desired type of token to reach at the beginning"""
    while 1:
        if tokenTx == MARKER_TOKEN_SILVER:
            print("searching a silver token")
            Move_to_token(tokenTx, 0.4)

            while (R.grab() == False) : # to ensure that we grab it
                print("failed to grab the silver token")
                Move_to_token(tokenTx, 0.3)
            
            print("grabbed a silver token")
            tokenTx = MARKER_TOKEN_GOLD
            print("time for a golden one")     

        else:
            Move_to_token(tokenTx, 0.5)
            R.release()
            print("released a silver token")
            drive(-10, 1.5) # to avoid hitting the robot with the released token
            turn(12, 2.5)		
            tokenTx = MARKER_TOKEN_SILVER
            print("time for a silver one")
```

## Troubleshooting ##
-------------------------

When running `python run.py <file>`, you may be presented with an error: `ImportError: No module named 'robot'`. This may be due to a conflict between sr.tools and sr.robot. To resolve, symlink simulator/sr/robot to the location of sr.tools.

On Ubuntu, this can be accomplished by:
* Find the location of srtools: `pip show sr.tools`
* Get the location. In my case this was `/usr/local/lib/python2.7/dist-packages`
* Create symlink: `ln -s path/to/simulator/sr/robot /usr/local/lib/python2.7/dist-packages/sr/`

