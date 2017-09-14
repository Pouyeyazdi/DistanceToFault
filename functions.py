#!/Users/pouye/anaconda/bin/python3.6  -tt
# Pouye Yazdi 13 Sep 2017

from math import cos, tan, radians
import numpy as np
import geopy
from geopy.distance import VincentyDistance
from geopy.distance import vincenty
from compassbearing import Calculate_Bearing
###############################################################################
def Fault_Proj(faultDisctionaty):
    #This function returns an list of vertices of projected surface as below:
    #[P1,P2,P3,P4]
    # Where Pi is a tuple (lat long)
    # [(float,float ) int]
    ######## Rjb needs Radial (Earth Radius) projection and Rrup needs Vertical (to the fault plane) projection:
    #
    #     P1jb  P1rup  P4jb            P4rup
    # -----|-----%-----|---------------%-------Surface
    #      |   %       |             %
    #      | %         |           %
    #      0...........|         %
    #        \\        |       %
    #          \\      |     %
    #   fault->  \\    |   %
    #              \\  | %
    #                \\|
    #  
    ########              
    origin = geopy.Point(faultDisctionaty.get('lat'), faultDisctionaty.get('long')) #Point reads latitue then longitude
    normal_to_strike=faultDisctionaty.get('azimuth')+90

    fault_projjb_vertex1=(faultDisctionaty.get('lat'), faultDisctionaty.get('long'))
    # Point 2
    destination = VincentyDistance(kilometers=faultDisctionaty.get('length')).destination(origin, faultDisctionaty.get('azimuth')) #(lat,long)
    fault_projjb_vertex2= (round(destination.latitude,3), round(destination.longitude,3))
    # Point 3
    proj_wide_size=faultDisctionaty.get('wide')*cos(radians(faultDisctionaty.get('dip')))
    destination = VincentyDistance(kilometers=proj_wide_size).destination(geopy.Point(fault_projjb_vertex2),normal_to_strike)
    fault_projjb_vertex3= (round(destination.latitude,3), round(destination.longitude,3))
    # Point 4
    destination = VincentyDistance(kilometers=proj_wide_size).destination(origin,normal_to_strike)
    fault_projjb_vertex4= (round(destination.latitude,3), round(destination.longitude,3))
    
    fault_projjb=[fault_projjb_vertex1,fault_projjb_vertex2,fault_projjb_vertex3,fault_projjb_vertex4]

    r=tan(radians(faultDisctionaty.get('dip')))*faultDisctionaty.get('Ztop')
    destination=VincentyDistance(kilometers=r).destination(origin,normal_to_strike)
    fault_projrup_vertex1= (round(destination.latitude,3), round(destination.longitude,3))
    # Point 2
    destination = VincentyDistance(kilometers=faultDisctionaty.get('length')).destination(geopy.Point(fault_projrup_vertex1), faultDisctionaty.get('azimuth'))
    fault_projrup_vertex2= (round(destination.latitude,3), round(destination.longitude,3))
    # Point 3
    proj_wide_size=faultDisctionaty.get('wide')/cos(radians(faultDisctionaty.get('dip')))
    destination = VincentyDistance(kilometers=proj_wide_size).destination(geopy.Point(fault_projrup_vertex2),normal_to_strike)
    fault_projrup_vertex3= (round(destination.latitude,3), round(destination.longitude,3))
    # Point 4
    destination = VincentyDistance(kilometers=proj_wide_size).destination(geopy.Point(fault_projrup_vertex1),normal_to_strike)
    fault_projrup_vertex4= (round(destination.latitude,3), round(destination.longitude,3))
    
    fault_projrup=[fault_projrup_vertex1,fault_projrup_vertex2,fault_projrup_vertex3,fault_projrup_vertex4] 

    return [fault_projjb,fault_projrup] # is two list of 4 tuples (lat,long)
###############################################################################
def Find_R_Zones(gridFilename,faultDisctionaty,RType):
    #This function returns an array of lists in vertical as below:
    #[['lat','long']] 'zone'
    # [float,float, int]
    # [float,float, int]
    # ...
    # [float,float, int]
    # The gridfilename icontains latitude (first column) and longitude (second column) of the gridpoints
    ######## Zones are as below:
    
    #          |           |
    #     1    |     2     |    3
    #          |           |
    #----------P2=========P3-----------
    #         ||+++++++++++|
    #         ||+++++++++++|
    #     4   ||+++++5+++++|    6
    #         ||+++++++++++|
    #         ||+++++++++++|
    #         ||+++++++++++|
    #----------P1=========P4-----------  
    #          |           |
    #    7     |     8     |    9
    #          |           |
    
    
    result=np.zeros((1,3))
    if RType=='Rjb':
        proj_type='radial'
        i=0
    if RType=='Rrup':
        proj_type='vertical'
        i=1
    if RType!='Rrup' and RType!='Rjb':
        print('ERR2:Unkown distance type')
        return  
        
    fault_proj_vertices=Fault_Proj(faultDisctionaty) # fault_proj_vertices are as (lat,long)
    strike=faultDisctionaty.get('azimuth')
    f=open(gridFilename, 'r') # grid file is given in input folder as (long,lat)
    r=open('gridZones_%s.txt'% RType,'w')
    r.writelines('The fault projection on surface is %s:\n' % proj_type)
    r.writelines('The projected vertices [P1,P2,P3,P4] are\n%s\n' % fault_proj_vertices[i])
    r.writelines('lat long zone\n')

   
    for line in f:
        grid_point=(round(float(line.split()[1]),3),round(float(line.split()[0]),3)) # fault_proj_vertices are as (lat,long) must be tuple
        bearing=round(Calculate_Bearing(fault_proj_vertices[i][0],grid_point)) 
        # Calculate_Bearing takes points as (lat,long) and gives alpha is in degree
        if bearing==strike or bearing==strike+360 or bearing==strike-360:
            #print('grid point is on the strike projection line +')
            if vincenty(fault_proj_vertices[i][0], grid_point).kilometers<=vincenty(fault_proj_vertices[i][0],fault_proj_vertices[i][1]).kilometers:
                zone=5
            else:
                zone=1
            alpha=0
        else:
            if bearing==strike-180 or bearing==strike+180:
                #print('grid point is on the strike projection line -')
                zone=7
                alpha=0
            else:
                if bearing<strike:
                    bearing=bearing+360                    
                alpha=bearing-strike
                if alpha>180: # 180<alpha<360
                    #print('grid point is on the foot-wall side')
                    if alpha<=270: # 180<alpha<=270
                        zone=7
                    else: # 270<alpha 
                        bearing_prime=round(Calculate_Bearing(fault_proj_vertices[i][1],grid_point)) 
                        if bearing_prime<strike:
                            bearing_prime=bearing_prime+360
                        alpha_prime=bearing_prime-strike 
                        if alpha_prime>=270:
                            zone=1
                        else:
                            if alpha_prime>180:
                                zone=4
                            else:
                                zone=5          
                else: # 0<alpha<180
                    #print('grid point is on the hanging-wall side')
                    if alpha==90:
                        if vincenty(fault_proj_vertices[i][0], grid_point).kilometers<=vincenty(fault_proj_vertices[i][0],fault_proj_vertices[i][3]).kilometers:
                            zone=5
                        else:
                            zone=9
                    else:
                        if alpha>90: # 90<alpha<180 zone 8 or 9
                            bearing_prime=round(Calculate_Bearing(fault_proj_vertices[i][3],grid_point))
                            if bearing_prime<strike:
                                bearing_prime=bearing_prime+360
                            alpha_prime=bearing_prime-strike 
                            if alpha_prime<=180:
                                zone=9
                            else:
                                if alpha_prime<270:
                                    zone=8
                                else:
                                    zone=5
                        else: # 0<alpha<90 zone 2,3,5,6
                            bearing_prime=round(Calculate_Bearing(fault_proj_vertices[i][2],grid_point))
                            if bearing_prime<strike:
                                bearing_prime=bearing_prime+360
                            alpha_prime=bearing_prime-strike 
                            if alpha_prime>270:
                                if alpha_prime<360:
                                    zone=2
                                else:
                                    zone=3
                            else:
                                if alpha_prime>=180:
                                    zone=5
                                else:
                                    if alpha_prime>90:
                                        zone=6
                                    else:
                                        zone=3   

        line=[grid_point[0],grid_point[1],int(zone)] 
        r.writelines('%8.3f %8.3f %1d\n' % (grid_point[0],grid_point[1],int(zone)))                              
        result= np.vstack([result,line])
    r.close()
    return [result[1:],fault_proj_vertices]

