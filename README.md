*******Quad Simulator using OpenGl and Pygame*********

An OpenGl implementation of a quadrotor simulator in python.

1). "glQuad_Simulation.py" implements a bird's eye view of a Back-stepping strategy for attitude control.

2). "glQuad_Simulation_v2.py" implements both third-person view and bird's eye view. It implelements a  Back-stepping strategy for attitude control of the quadrotor.
    Controls:-
      Press 'Spacebar' to increase the throttle and 'Left Control' key to decease the throttle
      Use Arrow Keys Left and right to increase or decrease Roll
      Use Arrow Keys Up and Down to increase or decrease Pitch
      Press 'Escape' key to end the simulation
      Press 'Shift' key to switch betwween the views

2). "glQuad_Simulation_v2.1.py" is a revamp of v2. It implements both third-person view and bird's eye view. It implelements a  Back-stepping strategy for both attitude control and position control of the quadrotor. The control inputs can be provided from a Joystick as well!! After the end of Simulation, various plots of position tracking, attiude tracking are plotted. RMS error in position tracking is printed to terminal.
    Keyboard Controls:-
      Press 'Spacebar' to increase the throttle and 'Left Control' key to decease the throttle
      Use Arrow Keys Left and right to move Quadrotor along East-West direction
      Use Arrow Keys Up and Down to move Quadrotor along North-South direction
      Use Keys 'A' and 'D' to increase or decrease Yaw
      Press 'Escape' key to end the simulation
      Press 'Shift' key to switch betwween the views
      
    Joytick Controls (tested on Logitech Attack 3. Make changes accordingly to ReadJoyInputs() to make it compatible with any other Joystick):-
      **Logitech Attack 3 has three axes (0-2) and 12 buttons (0-11)
      Move Axis-2 to increase/decrease the throttle
      Move Axis-0 to increase or decrease Roll
      Move Axis-1 to increase or decrease Pitch
      Press Buttons '8' and '7' to increase or decrease Yaw
      Press Button-2 to end the simulation and plot the relevant statistics
      Press Button-0 to switch betwween the views


