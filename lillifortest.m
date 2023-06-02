alpha_ctrl=[2,3,2,6,4,2,4,5,5,6,2,8,4,3,4,2,3,4,5,6,8,3,4,5,2,4,5,2,2,3];
alpha_test=[0,0,0,2,0,7,0,0,2,0,2,1,1,2,0,4,0,1,1,3,0,0,0,2,3,1,6,2,0,0];
betha_ctrl=[3,3,3,1,2,1,2,3,3,3,0,2,3,3,0,3,2,3,3,3,3,1,3,2,1,3,3,3,3,3];
betha_test=[2,0,0,3,1,7,0,0,2,0,3,0,4,3,0,5,0,0,0,6,0,1,0,1,3,0,6,6,2,0];
L_a_c=lillietest(alpha_ctrl)
L_a_t=lillietest(alpha_test)
L_b_c=lillietest(betha_ctrl)
L_b_t=lillietest(betha_test)