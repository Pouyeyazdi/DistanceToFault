#!/Users/pouye/anaconda/bin/python3.6  -tt
# Pouye Yazdi 13 sep 2017



import sys 
print ('***** Python version: ******\n'+sys.version+'\n****************************')
import numpy as np
import os 
from distance import Zone_Based_Distance


# Reading fault parameters from given file (when running : sys.argv[1])
fault_dict={}
def Cat_Fault(faultFilename):
    if os.path.exists('inputs/'+faultFilename)==False:
        print('ERR: Unknown fault file')
    else:
        f=open(os.path.join(os.path.abspath('inputs'),faultFilename), 'r')
        lines=f.readlines()
        fault_dict['long']=float(lines[0].split()[0])
        fault_dict['lat']=float(lines[1].split()[0])
        fault_dict['azimuth']=float(lines[2].split()[0])
        fault_dict['dip']=float(lines[3].split()[0])
        fault_dict['Ztop']=float(lines[4].split()[0])
        fault_dict['hypocenter']=float(lines[5].split()[0])
        fault_dict['mechanism']=lines[6].split()[0]
        fault_dict['length']=float(lines[7].split()[0])
        fault_dict['wide']=float(lines[8].split()[0])
        f.close()
        print('Fault characteristics:')  
        for key in fault_dict:
            print('%s : %s'% (key,fault_dict[key]))
        print('----------------------')
        return fault_dict            
            
            
def main():
    Cat_Fault(sys.argv[1]) #argv[1] means the item 1 in command line which would be the fault_filename we give
    # Check if the grid file exists. No dynamic name --> we only have one grid file: grid.txt
    grid_filename='gridLorca.txt' 
    if os.path.exists('inputs/'+grid_filename)==False:
        print('ERR: The grid file does not exist')
    else: 
        distance_type='Rrup' 
        print('The distance type to be calculated is: %s'%distance_type)
        grid_zone_distance=Zone_Based_Distance(os.path.join(os.path.abspath('inputs'),grid_filename),fault_dict,distance_type)
        size_of_grid=np.shape(grid_zone_distance)[0]
        d=open('%s_distances.txt'%distance_type,'w+')
        for i in range(size_of_grid):
            j=i*4
            data=np.take(grid_zone_distance,[j,j+1,j+2,j+3])
            d.writelines('%8.3f %8.3f %d %12.6f\n'% (data[0,0],data[0,1],data[0,2],data[0,3])) 
        print('Find the result in "%s_distances.txt"'%distance_type)
        print('Total number of grid-points: %d'%size_of_grid)
if __name__=='__main__':
    main()
        

        
