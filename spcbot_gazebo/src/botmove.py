#!/usr/bin/env python
import rospy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
import tf
import math
import time

pi = 22/7



def callback(data):
    global x
    global y, nYaw,yaw
    x = data.pose.pose.position.x
    y = data.pose.pose.position.y
    (roll, pitch, yaw) = tf.transformations.euler_from_quaternion([data.pose.pose.orientation.x, data.pose.pose.orientation.y, data.pose.pose.orientation.z, data.pose.pose.orientation.w])
    nYaw = yaw
    #rospy.loginfo('x: {}, y: {} yaw: {}'.format(x, y, nYaw))

def go_to_goal(x_goal, y_goal):
    global x
    global y, nYaw

    velocity_message = Twist()
    
    while (True):
        K_linear = 0.09 
        distance = abs(math.sqrt(((x_goal-x) ** 2) + ((y_goal-y) ** 2)))

        linear_speed = distance * K_linear


        K_angular = 0.7
        desired_angle_goal = math.atan2(y_goal-y, x_goal-x)
        angular_speed = (desired_angle_goal-nYaw)*K_angular

        velocity_message.linear.x = linear_speed
        velocity_message.angular.z = angular_speed

        velocity_publisher.publish(velocity_message)
        
        #print velocity_message.linear.x
        #print velocity_message.angular.z
        print 'x=', x, 'y=',y, 'dis: ',distance


        if (distance <0.5):
            velocity_message.linear.x = 0.0
            velocity_message.angular.z = 0.0
            velocity_publisher.publish(velocity_message)
            break

def setDesiredOrientation(desired_angle_radians):
    relative_angle_radians = desired_angle_radians - yaw
    if relative_angle_radians < 0:
        clockwise = 1
    else:
        clockwise = 0
    print relative_angle_radians*180/pi
    print desired_angle_radians*180/pi
    rotate(7 ,math.degrees(abs(relative_angle_radians)), clockwise)

def rotate (angular_speed_degree, relative_angle_degree, clockwise):
    global x
    global y, nYaw,yaw
    
    velocity_message = Twist()
    velocity_message.linear.x=0
    velocity_message.linear.y=0
    velocity_message.linear.z=0
    velocity_message.angular.x=0
    velocity_message.angular.y=0
    velocity_message.angular.z=0

    #get current location 
    theta0=yaw
    angular_speed=math.radians(abs(angular_speed_degree))

    if (clockwise):
        velocity_message.angular.z =-abs(angular_speed)
    else:
        velocity_message.angular.z =abs(angular_speed)

    angle_moved = 0.0
    loop_rate = rospy.Rate(10) # we publish the velocity at 10 Hz (10 times a second)    
    cmd_vel_topic='cmd_vel'
    velocity_publisher = rospy.Publisher(cmd_vel_topic, Twist, queue_size=10)

    t0 = rospy.Time.now().to_sec()

    while True :
        rospy.loginfo('x: {}, y: {} yaw: {}'.format(x, y, nYaw*180/pi))
        velocity_publisher.publish(velocity_message)

        t1 = rospy.Time.now().to_sec()
        current_angle_degree = (t1-t0)*angular_speed_degree
        loop_rate.sleep()


                       
        if  (current_angle_degree>relative_angle_degree):
            rospy.loginfo("reached")
            break

    #finally, stop the robot when the distance is moved
    velocity_message.angular.z =0
    velocity_publisher.publish(velocity_message)

def move(speed, distance, is_forward):
        #declare a Twist message to send velocity commands
        velocity_message = Twist()
        #get current location 
        global x, y,nYaw,yaw
        x0=x
        y0=y
       
        if (is_forward):
            velocity_message.linear.x =abs(speed)
        else:
        	velocity_message.linear.x =-abs(speed)

        distance_moved = 0.0
        loop_rate = rospy.Rate(10) # we publish the velocity at 10 Hz (10 times a second)    
        cmd_vel_topic='cmd_vel'
        velocity_publisher = rospy.Publisher(cmd_vel_topic, Twist, queue_size=10)

        while True :
                rospy.loginfo('x: {}, y: {} yaw: {}'.format(x, y, nYaw*180/pi))
                velocity_publisher.publish(velocity_message)

                loop_rate.sleep()
                
                #rospy.Duration(1.0)
                
                distance_moved = abs(0.5 * math.sqrt(((x-x0) ** 2) + ((y-y0) ** 2)))
                print  distance_moved               
                if  not (distance_moved<distance):
                    rospy.loginfo("reached")
                    break
        
        #finally, stop the robot when the distance is moved
        velocity_message.linear.x =0
        velocity_publisher.publish(velocity_message)

    
if __name__ == '__main__':
    try:
        rospy.init_node('loc_monitor', anonymous=True)
        #cmd_vel_topic='/gazebo/cmd_vel'
        #rospy.loginfo('x: {}, y: {} yaw: {}'.format(x, y, nYaw))
        velocity_publisher = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        
        rospy.Subscriber("/odom", Odometry, callback)
        time.sleep(2)
        
        xx = input("Enter locX:")
        yy = input("Enter locY:")
        gx = float(xx)
        gy = float(yy)
        go_to_goal(gx, gy)
        
        
        yy = input("Enter An:")
        gy = float(yy)
        aRad = gy*pi/180
        setDesiredOrientation(aRad)
        
        
        yy = input("Enter Dis:")
        gy = float(yy)
        if gy>0:
            move(0.3, gy, True)
        else:
            move(0.3, gy, False)
        
    except rospy.ROSInterruptException:
        rospy.ROSInterruptException