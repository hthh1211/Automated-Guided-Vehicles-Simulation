import OrderGeneration as OG
import copy
import AuxiliaryModule
import os
import configparser
import random

class myexception(Exception):
    def _ini_(self,error):
        self.error=error
    def _str_(self):
        return self.error


def picking_task_manager(item_line_possibility,Item_pod_Layer,pod_layer_Item,out_stations,columnumber,num_lines,static_shelves,unbooked_static_shelves,picking_task_info):
    item_selected=[]
    stationi_picking_info_temp=[]
    for i_station in range(1,len(out_stations)+1):
        if i_station%2==1:
            try:
                stationi_picking_info_temp=[x for x in picking_task_info if x[0] == out_stations[i_station - 1]][0]#[站台地点，站台排队待拣物品耗费时间,[item_selected],货架1
            except Exception as e:
                print('stationi_picking_info_temp',stationi_picking_info_temp,repr(e))
            if len(stationi_picking_info_temp)>=4:
                pass
            else:
                item_selected = OG.random_order_generation(item_line_possibility, Item_pod_Layer, num_lines)
                try:
                    pod_selection=pod_selecion_for_picking_station(item_selected, Item_pod_Layer, pod_layer_Item, out_stations[i_station - 1],static_shelves,unbooked_static_shelves, columnumber)
                except Exception as e:
                    pod_selection=None
                if pod_selection is None:
                     print('pod selection is none:',item_selected)
        #               aaa=pod_layer_Item[pod_selection[0]]
        #                 pod_selection = pod_selecion_for_picking_station(item_selected, Item_pod_Layer, pod_layer_Item, out_stations[i_station - 1],static_shelves,unbooked_static_shelves, columnumber)
                else:
                    try:
                        picking_task_info_new=[out_stations[i_station - 1],0]+[item_selected]+pod_selection
                        picking_task_info.remove(stationi_picking_info_temp)
                        picking_task_info.append(picking_task_info_new) #站台地点，站台排队待拣货物拣货时长，[需求物品信息]，货架编号1,货架编号2,
                    except Exception as e:
                        print('picking_task_info_new'+''+'picking_task_info')


#########################################################Picking Pod Selection##########################################################
def pod_selecion_for_picking_station(item_selected,Item_pod_Layer,pod_layer_Item,station,static_shelves,unbooked_static_shelves,columnumber):
     pod_selected=[]
     station_x,station_y=AuxiliaryModule.convert_vertex_to_coordinate(columnumber,station)
     all_pods_info=[]
     item_selected_temp=copy.deepcopy(item_selected) #[物品编号,物品需求数目]
     for eachelement in item_selected_temp:
         all_item_location=Item_pod_Layer['item_' + str(eachelement[0])][1:]
         for eachpod in all_item_location:
             The_pods_info=list(x for x in all_pods_info if x[0][0]==eachpod[0])
             if len(The_pods_info)==0:
                if eachpod[0] in unbooked_static_shelves:
                   pod_x,pod_y=AuxiliaryModule.convert_vertex_to_coordinate(columnumber,static_shelves[eachpod[0]])
                   station_pod_estimated_distance=abs(pod_x-station_x)+abs(pod_y-station_y)
                else:
                   station_pod_estimated_distance=0
                NumDesiredItemsInPod=sum(list(x[2] for x in pod_layer_Item[eachpod[0]] if x[1]=='item_'+str(eachelement[0])))
                all_pods_info.append([[eachpod[0],station_pod_estimated_distance],[eachelement[0],NumDesiredItemsInPod]]) #货架编号，货架站台距离，物品编号，货架中该物品数目
             else:
                item_num_=[x[1:] for x in  all_pods_info if x[0][0]==eachpod[0]][0]
                item_name=list(y[0] for y in item_num_)
                if eachelement[0] not in item_name:
                    NumDesiredItemsInPod=sum(list(x[2] for x in pod_layer_Item[eachpod[0]] if x[1]=='item_'+str(eachelement[0])))
                    IndexDesiredPod=list(all_pods_info.index(x) for x in all_pods_info if x[0][0]==eachpod[0])[0]
                    all_pods_info[IndexDesiredPod].append([eachelement[0],NumDesiredItemsInPod])
     all_pods_info=sorted(all_pods_info,key=lambda x:x[0][1])
     NumItemsSelected=len(item_selected_temp)
     pods_with_one_trip=[x for x in all_pods_info if get_items_with_adequate_amount(x,item_selected_temp)==NumItemsSelected]
     if pods_with_one_trip:
         return [pods_with_one_trip[0][0][0]]
     all_pods_info_temp = copy.deepcopy(all_pods_info)
     for i_numitem in range(1,NumItemsSelected+1):
         pods_with_two_trips = [x for x in all_pods_info if get_items_with_adequate_amount(x, item_selected_temp) == (NumItemsSelected-i_numitem)]
         for first_pod in pods_with_two_trips:
             all_pods_info_temp.remove(first_pod)
             for second_pod in all_pods_info_temp:
                 pods_selected=[]
                 pods_selected.append(first_pod)
                 pods_selected.append(second_pod)
                 if AdequateItemsInPods(pods_selected,item_selected_temp):
                     return [first_pod[0][0],second_pod[0][0]]
     pods_selected=[]
     for pod in all_pods_info:
         if HasDesiredItemsInPod(pod, item_selected_temp):
             pods_selected.append(pod)
             if IsPodsHaveAdequateItems(pods_selected, item_selected_temp):
                 return [x[0][0] for x in pods_selected] #[货架编号，等效lines数],[货架编号。。。。
     return None


def get_items_with_adequate_amount(pod_info,item_selected):
    Item_info=pod_info[1:]
    items_with_large_amount=0
    for eachitem in Item_info:
        if eachitem[1]>=[x[1] for x in item_selected if x[0]==eachitem[0]][0]:
            items_with_large_amount=items_with_large_amount+1
    return items_with_large_amount

def IsPodsHaveAdequateItems(pods_selected,item_selected_temp):
    HaveAdequateItems=True
    local_item_selected=copy.deepcopy(item_selected_temp)
    for eachitem in local_item_selected:
        ItemsSupplied=sum([sum([y[1] for y in x[1:] if y[0]==eachitem[0]]) for x in pods_selected])
        if ItemsSupplied<eachitem[1]:
            HaveAdequateItems=False
        else:
            item_selected_temp.remove(eachitem)
    return HaveAdequateItems

def HasDesiredItemsInPod(pod,item_selected_temp):
    for eachitem in item_selected_temp:
        if [x for x in pod if x[0]==eachitem[0]]:
            return True
    return False

def AdequateItemsInPods(pods_selected,item_selected_temp):
    for eachitem in item_selected_temp:
        ItemsSupplied=sum([sum([y[1] for y in x[1:] if y[0]==eachitem[0]]) for x in pods_selected])
        if ItemsSupplied<eachitem[1]:
            return False
    return True


def replenishing_task_manager(replen_stations,pod_called_count_for_replen,replenishing_task_info,replenishing_time):
    if not [x for x in replenishing_task_info if len(x)>=3]:
        for i_station in range(1,len(replen_stations)+1):
            if i_station%2==0:
                total_count = 0
                for i_pod in range(1, len(pod_called_count_for_replen) + 1):
                    total_count = pod_called_count_for_replen[i_pod] + total_count
                if total_count>0:
                    pod_called_count_array = []
                    for i_pod in range(1, len(pod_called_count_for_replen) + 1):
                        pod_called_count_array.append([i_pod, pod_called_count_for_replen[i_pod] / total_count])
                    OG.random_replen_order_generation(pod_called_count_array,total_count, pod_called_count_for_replen,replenishing_task_info, replen_stations,i_station,replenishing_time)

