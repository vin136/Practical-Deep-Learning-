
# coding: utf-8

# In[ ]:

#usage : eg-> python assignment.py -i ./dog.jpg -p 374,498 -s 2 -k True


import cv2
import argparse
import numpy as np






def my_linspace(start,stop,num):
    step = (stop-start)/(num-1)
    i = 0
    while(i != num):
        yield start + step*i
        i = i+1

        
# class my_linspace(collections.abc.Sequence): #subclass from abc.seq to get all the goodness of python bulit in 
#     #sequences.......

    
#     def __init__(self, start, stop, num):
#         if not isinstance(num, numbers.Integral) or num <= 1:
#             raise ValueError('num must be an integer > 1')
#         self.start, self.stop, self.num = start, stop, num
#         self.step = (stop-start)/(num-1)
#     def __len__(self):
#         return self.num
#     #Let's make it slicable..........
#     def __getitem__(self, i):
#         if isinstance(i, slice):
#             return [self[x] for x in range(*i.indices(len(self)))]
#         if i < 0:
#             i = self.num + i
#         if i >= self.num:
#             raise IndexError('linspace object index out of range')
#         if i == self.num-1:
#             return self.stop
#         return self.start + i*self.step
#     #let's get a good representaion...
#     def __repr__(self):
#         return '{}({}, {}, {})'.format(type(self).__name__,
#                                        self.start, self.stop, self.num)
#     def __eq__(self, other):
#         if not isinstance(other, linspace):
#             return False
#         return ((self.start, self.stop, self.num) ==
#                 (other.start, other.stop, other.num))
#     def __ne__(self, other):
#         return not self==other
#     #let's make it hashable : now we can even use it as a dictionary key.....
#     def __hash__(self):
#         return hash((type(self), self.start, self.stop, self.num))
#     #ok ...that's enough fun ...let's get down to business now.......
    
    


def from_iterable(iterables):
    for it in iterables:
        for element in it:
            yield element
    
    
def simple_interpolate(row,count,k_times= False):
            
    len_row = len(row)
    new_row = []
    
    if k_times:
        for i in range(len_row-1):
            new_row.append(list(my_linspace(row[i],row[i+1],count+1)))
        
    else:
        for i in range(len_row-1):
            new_row.append([row[i]] + [(row[i]+row[i+1])/2]*count)
    new_row.append([row[-1]])   
    #return list(it.chain.from_iterable(new_row))
    return list(from_iterable(new_row))  
  




def invert(mat):
    return [list(ele) for ele in zip(*mat)]

#expands a channel row-wise
def row_expand(channel,scale,k_times):
    row_expd_chnl = []
    
    for row in channel:
        row_expd_chnl.append(simple_interpolate(row,scale,k_times = k_times))
    #we have row expanded the channel now let's column expand the channel
    
    
    return row_expd_chnl


def channel_expand(chnl,scale,k_times = False):
    row_wise = row_expand(chnl,scale,k_times)
    return invert(row_expand(invert(row_wise),scale,k_times)) 




def get_range(id,new_total,old_total):
    check = old_total//2
    
    if id-check>=0 and id + check <= new_total:
        return id-check,id+check
    if id-check < 0:
        return 0,old_total
    else:
        return new_total-old_total,new_total
        
         
    
    


def get_sample(chnl,row_ind,col_ind,scale,k_times = False):
    new_chnl = channel_expand(chnl,scale,k_times)
    #return new_chnl
    max_old_row_id = len(chnl) - 1
    max_old_col_id = len(chnl[0]) - 1
    max_new_row_id = len(new_chnl) - 1
    max_new_col_id = len(new_chnl[0]) - 1
    if k_times:
        scale = scale - 1
    assert row_ind <= max_old_row_id,'row index out of bound'
    row_rg = get_range((row_ind*scale )+ row_ind,max_new_row_id,max_old_row_id)

    assert col_ind <= max_old_col_id,'column index out of bound'
    col_rg = get_range((col_ind*scale )+ col_ind,max_new_col_id,max_old_col_id)
    
    sample = [new_chnl[i][col_rg[0]:col_rg[1]+1] for i in range(row_rg[0],row_rg[1]+1)]
    
    return sample
    #return row_rg,col_rg,new_chnl


    
def zoomed(img,row_ind,col_ind,scale,k_times = False):
    channels = [img[:,:,i].tolist() for i in range(3)]
    new_channels = [get_sample(channel,row_ind,col_ind,scale,k_times = k_times) for channel in channels ]
    return np.uint(np.stack(new_channels,axis = 2))    




if __name__=="__main__":
    
    
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", help="Path to input image", required=True)
    ap.add_argument("-p", "--pivot-point", help="Pivot point coordinates (note indexing starts from 0) x, y separated by comma (,)", required=True)
    ap.add_argument("-s", "--scale", help="Scale to zoom", type=int, required=True)
    ap.add_argument("-k","--ktimes", help= "Ktimes algorithm", type = bool,required = True)
    args = vars(ap.parse_args())

    image_path = args["image"]
    x, y = map(int, args["pivot_point"].split(","))
    scale = args["scale"]
    image = cv2.imread(image_path)
    
    
    k_times = args["ktimes"]
    final_img = zoomed(image,x,y,scale,k_times = k_times)
    
    cv2.imwrite("zoomed_image.png", np.array(final_img, dtype="uint8"))




