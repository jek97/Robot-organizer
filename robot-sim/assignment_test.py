from __future__ import print_function

import time
from sr.robot import *
import math

"""
this program control the motion of a simple differential robots in a 2D plane, in which a series of golden and silver token are disposed rispectively in an outer bigger circle and a inner smaller one.
the task of the robot is to pick all the silver token and move them near a golden one.
"""


a_th = 2.0
""" float: Threshold for the control of the orientation for the grasping error"""

R = Robot()
""" instance of the class Robot"""

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
                Tg1 = S_y[j][0] * math.sin((S_y[j][1] - S_x[i][1]) * (math.pi / 180)) # projection of the token of type different from tokenTx that i don't want to hit, on the normal respect the direction to the token Tx ( so if it's less then half the track gouge it would be hitted)
            except:
                Tg1 = 10
            
            if D <= t or (abs(Tg1) < 0.4 and S_y[j][0] < S_x[i][0]) : # in both the cases...
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
            drive(20, 0.5)
        elif -90 < rot_y < -a_th:
            """ in this case to allign with the token we've to turn left a bit"""
            print("left a bit...")
            turn(-1, 0.5)
        elif 90 > rot_y > a_th:
            """ in this case to allign with the token we've to turn right a bit"""
            print("right a bit...")
            turn(3, 0.5)
        elif dist >= 1000 or rot_y >= 1000 :
            turn(10, 0.5) # no token remained in the list turn around to find one
            print("lost the token")


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
            drive(-20, 1.5) # to avoid hitting the robot with the released token
            turn(12, 2.5)		
            tokenTx = MARKER_TOKEN_SILVER
            print("time for a silver one")
main()
