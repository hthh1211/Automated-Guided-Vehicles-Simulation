import random
import AuxiliaryModule
import copy
class myexception(Exception):
    def _ini_(self,error):
        self.error=error
    def _str_(self):
        return self.error

def states_update(agv_current_status,agv_current_positions,agv_target_positions,agv_with_shelves,agv_destination_station,
                  unbooked_static_shelves,booked_static_shelves,moving_shelves,static_shelves,agv_seq_no,vertex_layer_shift,vacant,unbooked_vacant,pod_for_picking_or_replening,node_distance,pod_called_count,pod_called_count_for_replen,
                  out_stations,buffer_list_dic,agv_number,pod_layer_Item,station_picking_tasks,picking_time_per_item,grid_step_time,picking_task_info,agv_target_pod,station_type,):
    for agv_seq_no in range(1, agv_number + 1):
        current_agv_status = agv_current_status[agv_seq_no - 1]
        if current_agv_status == 'in buffer list selection':
            if agv_seq_no in moving_shelves.keys():
               pass
            else:
                agv_picking_task_info= [x for x in booked_static_shelves if x[0]==agv_seq_no][0]
                moving_shelves[agv_seq_no] = copy.deepcopy(agv_picking_task_info[1:])#货架号，站台地点，拣货时间
                if station_type[moving_shelves[agv_seq_no][1]] == '拣货台':
                    pod_called_count[moving_shelves[agv_seq_no][0]] = pod_called_count[moving_shelves[agv_seq_no][0]] + 1
                pod_for_picking_or_replening.append([agv_seq_no,moving_shelves[agv_seq_no][0],pod_called_count[moving_shelves[agv_seq_no][0]]]) #agv号，货架号，货架被叫次数
                booked_static_shelves.remove(agv_picking_task_info)
                agv_with_shelves.append(agv_seq_no)
                vacant.append(static_shelves[moving_shelves[agv_seq_no][0]])
                unbooked_vacant.append([static_shelves[moving_shelves[agv_seq_no][0]],node_distance[static_shelves[moving_shelves[agv_seq_no][0]]][0]])
                if moving_shelves[agv_seq_no][0] in static_shelves.keys():
                   del static_shelves[moving_shelves[agv_seq_no][0]]
                if moving_shelves[agv_seq_no][0] in unbooked_static_shelves:
                    unbooked_static_shelves.remove(moving_shelves[agv_seq_no][0])
            agv_destination_station[agv_seq_no - 1] = moving_shelves[agv_seq_no][1] #默认选第一个站台，但是前提是站台是合理排序的
            if agv_destination_station[agv_seq_no - 1] in station_picking_tasks.keys():
                station_picking_tasks[agv_destination_station[agv_seq_no - 1]].append([agv_seq_no,moving_shelves[agv_seq_no][0],moving_shelves[agv_seq_no][2]])
            else:
                station_picking_tasks[agv_destination_station[agv_seq_no - 1]]=[[agv_seq_no, moving_shelves[agv_seq_no][0], moving_shelves[agv_seq_no][2]]]#agv号，货架号，拣货时间
            agv_target_pod[agv_seq_no - 1]=None
            agv_target_positions[agv_seq_no - 1] = buffer_list_dic[agv_destination_station[agv_seq_no - 1]][0]
            agv_current_status[agv_seq_no - 1] = 'to in buffer list of station'
        elif current_agv_status == 'station selection':
            agv_target_positions[agv_seq_no - 1] = agv_destination_station[agv_seq_no - 1]
            agv_current_status[agv_seq_no - 1] = 'to station'
        elif agv_current_status[agv_seq_no - 1] == 'picking or replenishing items':
            station_all_picking_info = station_picking_tasks[agv_destination_station[agv_seq_no - 1]]
            index_picking_info = [station_all_picking_info.index(x) for x in station_all_picking_info if x[0] == agv_seq_no and x[1] == moving_shelves[agv_seq_no][0]][0]
            station_picking_tasks[agv_destination_station[agv_seq_no - 1]][index_picking_info][2]=int(station_picking_tasks[agv_destination_station[agv_seq_no - 1]][index_picking_info][2]-grid_step_time)
        elif agv_current_status[agv_seq_no - 1] == 'out buffer list selection':
            agv_target_positions[agv_seq_no - 1] = buffer_list_dic[agv_destination_station[agv_seq_no - 1]][-1]
            if station_type[moving_shelves[agv_seq_no][1]] == '拣货台':
                pod_called_count_for_replen[moving_shelves[agv_seq_no][0]] = pod_called_count_for_replen[moving_shelves[agv_seq_no][0]] + 1
            agv_current_status[agv_seq_no - 1] = 'to out buffer list of station'
        elif current_agv_status == 'Pod Storage Selection':
            pod_for_picking_or_replening.sort(key=lambda x:(x[2],x[0]),reverse=True) #先按照历史呼叫次数排名，后按照agv号排名，由高到低
            pod_rank=[pod_for_picking_or_replening.index(x) for x in pod_for_picking_or_replening if x[0]==agv_seq_no][0]
            unbooked_vacant.sort(key=lambda x:x[1],reverse=False)
            agv_target_positions[agv_seq_no - 1] = unbooked_vacant[pod_rank][0]
            del unbooked_vacant[pod_rank]
            pod_for_picking_or_replening.remove([agv_seq_no, moving_shelves[agv_seq_no][0],pod_called_count[moving_shelves[agv_seq_no][0]]])  # agv号，货架号，货架被叫次数
            agv_current_status[agv_seq_no - 1] = 'to unoccupied spots by static shelves'
        elif agv_current_status[agv_seq_no - 1] == 'shelves have been unloaded':
            static_shelves[moving_shelves[agv_seq_no][0]] = agv_target_positions[agv_seq_no - 1]
            unbooked_static_shelves.append(moving_shelves[agv_seq_no][0])
            del moving_shelves[agv_seq_no]
            agv_with_shelves.remove(agv_seq_no)
            vacant.remove(agv_target_positions[agv_seq_no - 1])
            if [agv_target_positions[agv_seq_no - 1],node_distance[agv_target_positions[agv_seq_no - 1]][0]] in unbooked_vacant:
                unbooked_vacant.remove([agv_target_positions[agv_seq_no - 1],node_distance[agv_target_positions[agv_seq_no - 1]][0]])



###########################################################################################robot allocation###############################################################################################
def Assign_Tasks_To_AGVs(agv_current_status,picking_task_info,replenishing_task_info,unbooked_static_shelves,static_shelves,agv_current_positions,agv_target_positions,pod_layer_Item,grid_step_time,picking_time_per_item,booked_static_shelves,column_number,moving_shelves,agv_target_pod,pod_status,out_stations,agv_destination_station,agv_seq_no):
 #按照先补货后拣货的顺序，此逻辑后续可优化
    tuple_agv_current_status=list(enumerate(agv_current_status))
    agv_seq_no_for_tasks=[x[0]+1 for x in tuple_agv_current_status if x[1]=='Pod Selection' or x[1]=='initial']
    waiting_agvs_list,future_waiting_agvs_list=waiting_agvs_in_picking_station(out_stations,agv_current_positions,agv_destination_station,agv_current_status,column_number)
    try:
        iteration_count=0

        if len(replenishing_task_info)>=1:
            replenishing_task_info_iterate=[x for x in replenishing_task_info if len(x)>=3]
        else:
            replenishing_task_info_iterate=[]
        if replenishing_task_info_iterate:
            replenishing_task_info_iterate=[x for x in replenishing_task_info_iterate if [y for y in x[2:] if y in unbooked_static_shelves and y not in pod_status.keys()]]
            task_assignment_indicator=[]
        if replenishing_task_info_iterate and agv_seq_no_for_tasks:
    #一个step由1个AGV补货一次
                for each_replenishing_task in replenishing_task_info_iterate:
                     station_x, station_y = AuxiliaryModule.convert_vertex_to_coordinate(column_number, each_replenishing_task[0])
                     for each_pod in each_replenishing_task[2:]:
                         pod_x, pod_y = AuxiliaryModule.convert_vertex_to_coordinate(column_number,static_shelves[each_pod])
                         for each_agv in agv_seq_no_for_tasks:
                             agv_point_x, agv_point_y = AuxiliaryModule.convert_vertex_to_coordinate(column_number,agv_current_positions[agv_seq_no - 1])
                             travel_time = (abs(pod_x - agv_point_x) + abs(pod_y - agv_point_y) + abs(station_x - pod_x) + abs(station_y - pod_y)) / grid_step_time
                             task_assignment_indicator.append([each_replenishing_task[0],each_pod,each_agv,travel_time,each_replenishing_task[1]])#补货台地点，货架号，agv号，搬运时间,补货时间
                task_assignment_indicator.sort(key=(lambda x:x[3]))
                chosen_replen_pod=task_assignment_indicator[0][1]
                chosen_replen_agv=task_assignment_indicator[0][2]
                station_vertex=task_assignment_indicator[0][0]
                etsimated_picking_time=task_assignment_indicator[0][4]
                booked_static_shelves.append([chosen_replen_agv, chosen_replen_pod, station_vertex, etsimated_picking_time])  # agv号，货架号，站台地点，拣货时间
                target_replenishing_task_info=[x for x in replenishing_task_info if x[0]==station_vertex][0]
                replenishing_task_info.remove(target_replenishing_task_info)
                target_replenishing_task_info_part1=target_replenishing_task_info[2:]
                target_replenishing_task_info_part1.remove(chosen_replen_pod)
                target_replenishing_task_info=target_replenishing_task_info[:2]+target_replenishing_task_info_part1
                replenishing_task_info.append(target_replenishing_task_info)
                agv_target_positions[chosen_replen_agv - 1] = static_shelves[chosen_replen_pod]
                agv_target_pod[chosen_replen_agv - 1] = chosen_replen_pod
                if chosen_replen_pod in unbooked_static_shelves:
                    unbooked_static_shelves.remove(chosen_replen_pod)
                agv_current_status[chosen_replen_agv - 1] = 'to shelves'
                agv_seq_no_for_tasks.remove(chosen_replen_agv)


        aaa=len(agv_seq_no_for_tasks)
        wuhh1=0
        if aaa<=5 and aaa>=1:
            wuhh1=1
        picking_task_info_iterate = [x for x in picking_task_info if len(x) >= 4]
        if picking_task_info_iterate:
            picking_task_info_iterate = [x for x in picking_task_info_iterate if [y for y in x[3:] if y in unbooked_static_shelves and y not in pod_status.keys()]]  # 假如picking_task_info中某一元素中的某一pod被包含在unbooked_static_shelves
        while agv_seq_no_for_tasks and picking_task_info_iterate:
            iteration_count=iteration_count+1
            if iteration_count>=300:
                raise myexception("error:the iteration count is over 300")
            task_assignment_indicator=[]
            picking_task_info_iterate=[x for x in picking_task_info if len(x)>=4]
            if picking_task_info_iterate:
                picking_task_info_iterate=[x for x in picking_task_info_iterate if [y for y in x[3:] if y in unbooked_static_shelves and y not in pod_status.keys()]] #假如picking_task_info中某一元素中的某一pod被包含在unbooked_static_shelves
            if picking_task_info_iterate:
                picking_task_info_iterate=rank_array(picking_task_info_iterate,waiting_agvs_list,future_waiting_agvs_list)
                target_picking_task_info=picking_task_info_iterate[0]
                target_picking_task_info_temp = copy.deepcopy(target_picking_task_info)
                station_vertex =target_picking_task_info[0]
                station_x,station_y=AuxiliaryModule.convert_vertex_to_coordinate(column_number,station_vertex)
                for each_Index_of_pod in target_picking_task_info[3:]:
                    if each_Index_of_pod in unbooked_static_shelves:
                        items_needed_in_this_pod=get_num_items_met_for_order_in_pod(target_picking_task_info_temp, each_Index_of_pod, pod_layer_Item)
                        pod_x,pod_y=AuxiliaryModule.convert_vertex_to_coordinate(column_number,static_shelves[each_Index_of_pod])
                        for agv_seq_no in agv_seq_no_for_tasks:
                            agv_point_x,agv_point_y=AuxiliaryModule.convert_vertex_to_coordinate(column_number,agv_current_positions[agv_seq_no-1])
                            travel_time=(abs(pod_x-agv_point_x)+abs(pod_y-agv_point_y)+abs(station_x-pod_x)+abs(station_y-pod_y))/grid_step_time
                            task_assignment_indicator.append([agv_seq_no,each_Index_of_pod,items_needed_in_this_pod,items_needed_in_this_pod/(travel_time+target_picking_task_info[1])])
                task_assignment_indicator=sorted(task_assignment_indicator,key=lambda x:x[3])
                chosen_pod=task_assignment_indicator[-1][1]
                chosen_agv=task_assignment_indicator[-1][0]
                items_needed=task_assignment_indicator[-1][2]
                etsimated_picking_time=items_needed * picking_time_per_item
                booked_static_shelves.append([chosen_agv,chosen_pod,station_vertex,etsimated_picking_time]) #agv号，货架号，站台地点，拣货时间
                picking_task_info.remove(target_picking_task_info)
                get_num_items_needed_in_pod(target_picking_task_info, chosen_pod, pod_layer_Item)
                target_picking_task_info[1] = int(target_picking_task_info[1] +etsimated_picking_time )
####################################remove chosen_pod#####################################################
                target_picking_task_info_part1 = target_picking_task_info[:3]
                target_picking_task_info_part2 = target_picking_task_info[3:]
                target_picking_task_info_part2.remove(chosen_pod)
                target_picking_task_info = target_picking_task_info_part1 + target_picking_task_info_part2
################################################################################################################
                picking_task_info.append(target_picking_task_info)
                agv_target_positions[chosen_agv - 1]=static_shelves[chosen_pod]
                agv_target_pod[chosen_agv-1]=chosen_pod
                if chosen_pod in unbooked_static_shelves:
                    unbooked_static_shelves.remove(chosen_pod)
                agv_current_status[chosen_agv - 1] = 'to shelves'
                agv_seq_no_for_tasks.remove(chosen_agv)

    except Exception as e:
        print(repr(e))
    except myexception as e:
        print(repr(e))

def Assign_tasks_to_station_hopping(moving_shelves,agv_seq_no,picking_task_info,replenishing_task_info,pod_layer_Item,picking_time_per_item,station_type):
    selection_count=1
    while selection_count<=2:
        if station_type[moving_shelves[agv_seq_no][1]]=='拣货台' and selection_count==1 or (station_type[moving_shelves[agv_seq_no][1]]=='补货台' and selection_count==2):
            Index_of_target_shelf = moving_shelves[agv_seq_no][0]
            qualified_picking_task= [x for x in picking_task_info if len(x)>=4]  # 此处应当添加站台访问顺序控制逻辑
            target_picking_task=[x for x in qualified_picking_task if Index_of_target_shelf in x[3:] and moving_shelves[agv_seq_no][1]!=x[0]]
            if target_picking_task:
                target_picking_task_info=target_picking_task[0]
                items_needed_in_pod=get_num_items_needed_in_pod(target_picking_task_info,Index_of_target_shelf,pod_layer_Item)
                moving_shelves[agv_seq_no] = [Index_of_target_shelf] + [target_picking_task_info[0]]+[items_needed_in_pod*picking_time_per_item]
                picking_task_info.remove(target_picking_task_info)
                get_num_items_needed_in_pod(target_picking_task_info, moving_shelves[agv_seq_no][0], pod_layer_Item)
                target_picking_task_info[1] = int(target_picking_task_info[1] + moving_shelves[agv_seq_no][2])
                ####################################remove chosen_pod#####################################################
                target_picking_task_info_part1 = target_picking_task_info[:3]
                target_picking_task_info_part2 = target_picking_task_info[3:]
                target_picking_task_info_part2.remove(moving_shelves[agv_seq_no][0])
                target_picking_task_info = target_picking_task_info_part1 + target_picking_task_info_part2
                ################################################################################################################
                picking_task_info.append(target_picking_task_info)
                return True
            else:
                selection_count = selection_count + 1
                if selection_count>=3:
                    return False
        elif station_type[moving_shelves[agv_seq_no][1]]=='补货台' and selection_count==1 or (station_type[moving_shelves[agv_seq_no][1]]=='拣货台' and selection_count==2):
            Index_of_target_shelf = moving_shelves[agv_seq_no][0]            # 货架号，站台地点，拣货时间
            qualified_replen_task=[x for x in replenishing_task_info if len(x)>=3]
            target_replenishing_task=[x for x in replenishing_task_info if Index_of_target_shelf in x[2:] and moving_shelves[agv_seq_no][1]!=x[0]]
            if target_replenishing_task:
                target_replenishing_task_info=target_replenishing_task[0] #此处因添加站台平衡控制
                moving_shelves[agv_seq_no]=[Index_of_target_shelf]+[target_replenishing_task_info[0]]+[target_replenishing_task_info[1]]
                replenishing_task_info.remove(target_replenishing_task_info)
                target_replenishing_task_info_part1 = target_replenishing_task_info[2:]
                target_replenishing_task_info_part1.remove(moving_shelves[agv_seq_no][0])
                target_replenishing_task_info = target_replenishing_task_info[:2] + target_replenishing_task_info_part1
                replenishing_task_info.append(target_replenishing_task_info)
                return True
            else:
                selection_count = selection_count + 1
                if selection_count>=3:
                    return False


def get_num_items_met_for_order_in_pod(target_picking_task_info_temp,Index_of_shelf,pod_layer_Item):
    items_needed_in_pod=0
     #站台地点，站台排队待拣货物拣货时长，[需求物品信息]，货架编号1,货架编号2...
    Item_selected=target_picking_task_info_temp[2]
    for each_item in Item_selected:
        NumDesiredItemsInPod = sum(list(x[2] for x in pod_layer_Item[Index_of_shelf] if x[1] == 'item_' + str(each_item[0])))
        if NumDesiredItemsInPod>each_item[1]:
            items_needed_in_pod=items_needed_in_pod+each_item[1]
        else:
            items_needed_in_pod=items_needed_in_pod+NumDesiredItemsInPod
    return items_needed_in_pod

def get_num_items_needed_in_pod(target_picking_task_info_temp,Index_of_pod,pod_layer_Item):
    items_needed_in_pod=0
     #站台地点，站台排队待拣货物拣货时长，[需求物品信息]，货架编号1,货架编号2...
    Item_selected=target_picking_task_info_temp[2]
    for each_item in Item_selected:
        NumDesiredItemsInPod = sum(list(x[2] for x in pod_layer_Item[Index_of_pod] if x[1] == 'item_' + str(each_item[0])))
        if NumDesiredItemsInPod>each_item[1]:
            each_item[1]=0
            items_needed_in_pod=items_needed_in_pod+each_item[1]
        else:
            each_item[1]=each_item[1]-NumDesiredItemsInPod
            items_needed_in_pod=items_needed_in_pod+NumDesiredItemsInPod
    return items_needed_in_pod

def rank_array(picking_task_info_iterate,waiting_agvs_list,future_waiting_agvs_list):
    new_array=[]
    discount_factor_waiting_list=0.5
    picking_task_info_station_picking_time=[x[:2]+[picking_task_info_iterate.index(x)]+[len(waiting_agvs_list[x[0]])] +[len(future_waiting_agvs_list)]for x in picking_task_info_iterate]
    picking_task_info_station_picking_time.sort(key=(lambda x:(x[3]+discount_factor_waiting_list*x[4],x[1])))
    for i_staion_picking_time in range(1,len(picking_task_info_station_picking_time)+1):
        index=picking_task_info_station_picking_time[i_staion_picking_time-1][2]
        new_array.append(picking_task_info_iterate[index])
    return new_array

def waiting_agvs_in_picking_station(out_stations,agv_current_positions,agv_destination_station,agv_current_status,column_number):
    distance_threhold=7
    waiting_agvs={}
    future_waiting_agvs={}
    for i_station in range(1,len(out_stations)+1):
        waiting_agvs[out_stations[i_station - 1]]=[]
        future_waiting_agvs[out_stations[i_station - 1]]=[]
        for agv_seq_no in range(1,len(agv_current_status)+1):
            agv_status=agv_current_status[agv_seq_no-1]
            if agv_destination_station[agv_seq_no - 1] == out_stations[i_station - 1]:
                if AuxiliaryModule.wall_street_distance(column_number,out_stations[i_station - 1],agv_current_positions[agv_seq_no-1])<distance_threhold:
                    if 'to in buffer list of station' in agv_status  or 'station selection' in agv_status or 'to station' in agv_status or 'picking or replenishing items' in agv_status:
                         waiting_agvs[out_stations[i_station - 1]].append(agv_seq_no)
                else:
                    if 'to shelves' in agv_status  or 'to in buffer list of station' in agv_status or 'in buffer list selection' in agv_status:
                        future_waiting_agvs[out_stations[i_station - 1]].append(agv_seq_no)

    return waiting_agvs,future_waiting_agvs