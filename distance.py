#!/Users/pouye/anaconda/bin/python3.6  -tt
# Pouye Yazdi 13 Sep 2017


from functions import Find_R_Zones
from math import sin, cos, radians, sqrt, pow
from geopy.distance import vincenty
from geopy.distance import VincentyDistance
import numpy as np
import pyproj
from shapely import geometry
import geopandas 



def Zone_Based_Distance(gridFilename,faultDisctionaty,RType):
    
    [grid,fault_proj_vertices]=Find_R_Zones(gridFilename,faultDisctionaty,RType)
    fault_Point1jb=fault_proj_vertices[0][0]
    fault_Point2jb=fault_proj_vertices[0][1]
    fault_Point3jb=fault_proj_vertices[0][2]
    fault_Point4jb=fault_proj_vertices[0][3]
    fault_Point1rup=fault_proj_vertices[1][0]
    fault_Point2rup=fault_proj_vertices[1][1]
    fault_Point3rup=fault_proj_vertices[1][2]
    fault_Point4rup=fault_proj_vertices[1][3]
    Ztop=faultDisctionaty.get('Ztop')
    Zdown=Ztop+faultDisctionaty.get('wide')*sin(radians(faultDisctionaty.get('dip')))
    Rtop=Ztop/cos(radians(faultDisctionaty.get('dip')))
    Rdown=Zdown/cos(radians(faultDisctionaty.get('dip')))
    X=Rtop/sin(radians(faultDisctionaty.get('dip')))
    oposite_strike=faultDisctionaty.get('azimuth')+180
    grid_matrix=np.matrix(grid)

    def Distance_Point_to_Line(P0,P1,P2):
        p=pyproj.Proj(proj='utm',zone=30, ellps='WGS84')    
        [point_x,point_y]=p(P0[1],P0[0]) #pyproj.Proj calls (long,lat)
        [line_Point1_x,line_Point1_y]=p(P1[1],P1[0])
        [line_Point2_x,line_Point2_y]=p(P2[1],P2[0])
        triangle=geometry.Polygon([(point_x,point_y),(line_Point1_x,line_Point1_y),(line_Point2_x,line_Point2_y)])
        g=geopandas.GeoSeries([triangle])
        D=(g.area[0]/(vincenty(P1, P2).kilometers))/500000
        return D
    
    def Rjb_Zone_1(gridPoint):
        Rjb=vincenty(gridPoint, fault_Point2jb).kilometers
        return Rjb
    def Rrup_Zone_1(gridPoint):
        R=Rjb_Zone_1(gridPoint)
        Rrup=sqrt(pow(Ztop,2)+pow(R,2))
        return Rrup
    #-----------------------------------------------------------------------
    def Rjb_Zone_2(gridPoint):
        Rjb=Distance_Point_to_Line(gridPoint,fault_Point2jb,fault_Point3jb)
        return Rjb
    def Rrup_Zone_2(gridPoint):
        R=Distance_Point_to_Line(gridPoint,fault_Point2rup,fault_Point3rup)
        dest=VincentyDistance(kilometers=R).destination(gridpoint,oposite_strike)
        Pm=(round(dest.latitude,3), round(dest.longitude,3))
        h=Rdown*((X+ vincenty(fault_Point2rup,Pm).kilometers)/(X+vincenty(fault_Point2rup,fault_Point3rup).kilometers))
        Rrup=sqrt(pow(h,2)+pow(R,2))
        return Rrup
    #-----------------------------------------------------------------------  
    def Rjb_Zone_3(gridPoint):
        Rjb=vincenty(gridPoint, fault_Point3jb).kilometers
        return Rjb
    def Rrup_Zone_3(gridPoint):
        R=Rjb_Zone_3(gridPoint)
        Rrup=sqrt(pow(Zdown,2)+pow(R,2))
        return Rrup
    #-----------------------------------------------------------------------
    def Rjb_Zone_4(gridPoint):
        Rjb=Distance_Point_to_Line(gridPoint,fault_Point1jb,fault_Point2jb)
        return Rjb
    def Rrup_Zone_4(gridPoint):
        Rrup=sqrt(pow(Rjb_Zone_4(gridPoint),2)+pow(Ztop,2))
        return Rrup
    #-----------------------------------------------------------------------
    def Rjb_Zone_5(gridPoint):
        return 0
    def Rrup_Zone_5(gridPoint):
        R=Distance_Point_to_Line(gridPoint,fault_Point1rup,fault_Point2rup)
        Rrup=Rdown*((X+R)/(X+vincenty(fault_Point1rup, fault_Point4rup).kilometers))
        return Rrup
    #-----------------------------------------------------------------------
    def Rjb_Zone_6(gridPoint):
        Rjb=Distance_Point_to_Line(gridPoint,fault_Point3jb,fault_Point4jb)
        return Rjb
    def Rrup_Zone_6(gridPoint):
        Rrup=sqrt(pow(Rjb_Zone_6(gridPoint),2)+pow(Zdown,2))
        return Rrup
     #-----------------------------------------------------------------------       
    def Rjb_Zone_7(gridPoint):
        Rjb=vincenty(gridPoint, fault_Point1jb).kilometers
        return Rjb
    def Rrup_Zone_7(gridPoint):
        R=Rjb_Zone_7(gridPoint)
        Rrup=sqrt(pow(Ztop,2)+pow(R,2))
        return Rrup
    #-----------------------------------------------------------------------
    def Rjb_Zone_8(gridPoint):
        Rjb=Distance_Point_to_Line(gridPoint,fault_Point1jb,fault_Point4jb)
        return Rjb
    def Rrup_Zone_8(gridPoint):
        R=Distance_Point_to_Line(gridPoint,fault_Point1rup,fault_Point4rup)
        dest=VincentyDistance(kilometers=R).destination(gridpoint,faultDisctionaty.get('azimuth'))
        Pm=(round(dest.latitude,3), round(dest.longitude,3))
        h=Rdown*((X+vincenty(fault_Point1rup, Pm).kilometers)/(X+vincenty(fault_Point1rup,fault_Point4rup).kilometers))
        Rrup=sqrt(pow(h,2)+pow(R,2))        
        return Rrup
    #-----------------------------------------------------------------------
    def Rjb_Zone_9(gridPoint):
        Rjb=vincenty(gridPoint, fault_Point4jb).kilometers
        return Rjb
    def Rrup_Zone_9(gridPoint):
        R=Rjb_Zone_9(gridPoint)
        Rrup=sqrt(pow(Zdown,2)+pow(R,2))
        return Rrup 
        
    
    s=np.shape(grid_matrix)[0] 
    distance_array=np.zeros((s,1))
    for z in range(1,10):        
        index=np.where(grid_matrix[:,2]==z)[0]
        if index.size:
            print('%3d grid-point in zone %d'%(index.size,z))
            for i in index:
                gridpoint=(grid_matrix[i,0],grid_matrix[i,1])
                distance=eval('%s_Zone_%d(gridpoint)'%(RType,z))
                distance_array[i,0]= distance
        else:
            print('  0 grid-point in zone %d'%z)
    grid_matrix= np.hstack([grid_matrix,distance_array])
    return grid_matrix
    #print(grid_matrix)
            
            
            
            