from __future__ import print_function

import time
from sr.robot import *

R = Robot()

d_tk= 0.4 #minimum distance to be able to grab the token
a_th= 2 #indicative range so that the robot can be aligned
token_grab = [] # list holding paired tokens in memory

def drive(speed, seconds): #through this function can advance the robot with a linear speed for an assigned time
    
    R.motors[0].m0.power = speed # left motor 0
    R.motors[0].m1.power = speed # right motor 1 
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed, seconds): #through this function can rotate the robot with an angular speed for an assigned time
    
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def find_silver_token(): #through this function find the silver token 
    
    dist=200
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER and check_token_grab(token.info.offset) == False: # if the token distance is less than 200, it is silvered and is not in the list:
            dist=token.dist
	    rot_y=token.rot_y
	    offset = token.info.offset
    if dist==200:
    	return -2, -2, -2 # return this if no token was found
    else:
   	return dist, rot_y, offset

def find_golden_token(): #through this function find the golden token
    
    dist=200
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD and check_token_grab(token.info.offset) == False: # if the token distance is less than 200, it is golden and is not in the list:
            dist=token.dist
	    rot_y=token.rot_y
	    offset = token.info.offset
    if dist==200:
	return -2, -2, -2 
    else:
   	return dist, rot_y, offset
   	
def add_token_grab(offset): # through this function store the tokens in the list
    global token_grab
    token_grab.append(offset)

def check_token_grab(offset): # through this function checking if the token is already in the list
    global token_grab
    for token in token_grab:
        if token == offset:
           return True
    return False
    
    
silver = True 

while 1:
    if len(token_grab) == 12: # if the list is full, the program terminates execution
        print("Game over bro..")
	exit()
    if silver == True: # if silver is True, than we look for a silver token, otherwise for a golden one
	dist, rot_y, offset = find_silver_token()
    else:
	dist, rot_y, offset = find_golden_token()
    if dist==-2: # if no token is detected, we make the robot turn 
	turn(10, 0.5)
    elif dist <= d_tk and silver == True: # if the current distance to the token is less than d_tk and the token is silvered:
        print("OKAY I FOUND IT!!")
        R.grab() # the robot grab the token 
        add_token_grab(offset) # the silver token is added to the list 
        drive(-20,1) # the robot backs away after taking the token 
	silver = not silver # we modify the value of the variable silver, so that in the next step we will look for the other type of token
    elif dist <= d_tk + 0.2 and silver == False: # if the current distance to the token is less than d_tk + 0.2 and the token is golden:
	print("Paired!")
    	R.release() # the robot release the silver token near the golden token 
    	add_token_grab(offset) # the golden token is added to the list
    	drive(-20,1)
    	silver = not silver      
    elif -a_th<= rot_y <= a_th: # if the robot is well aligned with the token, we go forward
	print("Wait...I'm coming")
        drive(20, 1)
    elif rot_y < -a_th: # if the robot is not well aligned with the token, we move it on the left or on the right
        print("Left a bit...")
        turn(-2, 0.5)
    elif rot_y > a_th:
        print("Right a bit...")
        turn(+2, 0.5)
    
