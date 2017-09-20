# Finding Rrup and Rjb to a fault plane

The geometry of fault plane is given in file **fault.txt** inside **"inputs"** directory as well as the grid file which includes the location of points in geodetic decimal-degree.

###**Functions in "functions.py" prepare the projection zones.** 

>_Fault\_Proj_ projects fault vertices on surface.

>1. Projection **vertical to the surface** for Rjb
2. Projection **vertical to the fault plane** for Rrup

>_Find\_R\_Zone_ asks for projection type and based on that gives the zone number (1,2,..9) in which each grid points is placed.
 
###**Function in "distance.py" calculates the given distance (Rjb or Rrup).** 
>_Zone\_Based\_Distance_ finds the distance based on the zone of each point 
