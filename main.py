    # -*- coding: UTF-8 -*-

import ConfigManager
import networkx
import graphics
import random
import AuxiliaryModule
import copy
import time
import os
import shutil
import result
import pylab
import math
import AGVAGENT
import CentralDispatchSystem as CDS
import StationAgent as SA
import pdb
def main():

    # config and map
    if os.path.exists(os.getcwd()+ "\\"+"SnapShots"):
        shutil.rmtree(os.getcwd()+ "\\"+"SnapShots")
    os.mkdir('SnapShots')
    vertex_layer_shift = ConfigManager.get_vertex_layer_shift() #
    map_original,map_nodes,node_distance,buffer_list_dic,boundary_nodes_x,boundary_nodes_y = ConfigManager.load_config() #buffer_list_dic:key is station vertex and value is buffer vertex
    conf = ConfigManager.ConfigPara() #
    conf.LoadConfigFromFile(map_nodes,buffer_list_dic)#
    conf.Print()
    result.background(boundary_nodes_x,boundary_nodes_y)

    grid_length = conf.grid_length
    column_number = conf.column_number
    row_number = conf.row_number
    agv_number = conf.agv_num
    agv_maxspeed = conf.agv_maxspeed
    agv_kinematic_parameter=conf.agv_kinematic
    picking_time_per_item=conf.picking_time_per_item
    grid_step_time = grid_length / agv_maxspeed

    out_stations = conf.out_station
    replen_stations=conf.replen_stations
    station_picking_tasks={}
    station_type={}

    agv_current_positions = []
    agv_path_segments=[]
    agv_motion_state=[] #x,y,Vx,Vy,r,W
    agv_current_status = []
    agv_target_positions = []
    agv_paths = []
    agv_paths_weight_sum=[]
    agv_info_for_map=[]
    agv_finished_package_count = []
    agv_unload_shelves_count=[]
    agv_wait_times = []
    pod_called_count = conf.pod_called_count # 统计各货架搬运次数
    pod_called_count_for_replen=conf.pod_called_count_for_replen
    pod_for_picking_or_replening=[]
    pods_for_dislocation={}
    pod_status={} #判断货架是否处于倒腾货架的状态
    out_station_package_count = []
    agv_destination_station=[]
    picking_task_info=[]
    replenishing_task_info=[]
    vacant=conf.unoccupied_vertex
    unbooked_vacant=[]
    agv_target_pod=[]
    moving_shelves={} #key is agv and value is the shelf it loads
    static_shelves=conf.initial_static_shelves_vertex #key is the shelf index and value is its location(Vertex)
    unbooked_static_shelves=copy.deepcopy(list(static_shelves.keys()))
    booked_static_shelves=[]
    agv_with_shelves=copy.deepcopy(list(moving_shelves.keys()))
    other_information={}
    replenishing_time_per_pod=conf.replenishing_time_per_pod
    call_interval_by_replen_station=conf.call_interval_by_replen_station
    edge_increased_weight=[]
    occupied_edge_increased_weight = 10000
    AGV_visit_station_count=0
    Average_visit_station_count=0

    waiting_counts_in_stations={}

    Item_pod_Layer=conf.Initial_Item_Layer
    pod_layer_Item=conf.Initial_Layer_Item
    Order_Line_selection=conf.Initial_Order_selection
    num_lines=conf.num_lines
    simulation_start_time = time.time()


    # 初始化参数数组
    for agv_seq_no in range(1, agv_number + 1):
        agv_finished_package_count.append(0)
        agv_unload_shelves_count.append(0)
        agv_wait_times.append(0)
        agv_target_pod.append(None)
        edge_increased_weight.append(occupied_edge_increased_weight)
        waiting_counts_in_stations[agv_seq_no]=[]
    for station_no in range(1, len(out_stations) + 1):
        out_station_package_count.append(0)
        picking_task_info.append([out_stations[station_no-1],0])
        station_type[out_stations[station_no-1]]='拣货台'
    for station_no in range(1,len(replen_stations)+1):
        replenishing_task_info.append([replen_stations[station_no-1]])
        station_type[replen_stations[station_no-1]]='补货台'

    # 初始化agv位置
    print('intializing agv positions...')
    for agv_seq_no in range(1, agv_number + 1):
        while (True):
            try:
                random_vertex = random.randint(1, column_number*row_number+1)
                if (map_original.has_node(random_vertex)==True):
                    conflict_index = agv_current_positions.index(random_vertex)
                    #print('index='+str(conflict_index)+' vertex='+str(random_vertex))
            except:
                break
        agv_current_positions.append(random_vertex)
        random_x,random_y=AuxiliaryModule.convert_vertex_to_coordinate(column_number,random_vertex)
        agv_motion_state.append([random_x,random_y,0,0,0,0])
        agv_path_segments.append([random_vertex])
        agv_current_status.append('initial') # initial, to in station; receiving package; to out station; dropping package; to charge station; in charge;
        agv_target_positions.append(random_vertex)
        agv_paths.append(None)
        agv_paths_weight_sum.append(None)
        agv_destination_station.append(None)



    # 去除agv静态占用的路径，仅移除到达AGV点的方向的路径，从AGV点出发的点无需移除--不懂
    path_incread_weight_per_agv = 1
    map_current = copy.deepcopy(map_original)
    for agv_seq_no in range(1, agv_number + 1):
        agv_info_for_map.append([agv_current_positions[agv_seq_no - 1],'initial']) #-1 means that this agv has not shelf on itself right now


    # simulate agv moving
    simulation_total_time = conf.simulation_time # seconds
    simulation_steps = int(simulation_total_time / grid_step_time)
    finished_package_count = 0
    waiting_count = 0
    agv_move_step_count = 0
    efficient_info = ''
    result.write_positions_to_file(column_number, agv_info_for_map,static_shelves,other_information,simulation_start_time) # 初始位置
    for step in range(1, simulation_steps):
        if step%call_interval_by_replen_station==0:
           SA.replenishing_task_manager(replen_stations, pod_called_count_for_replen, replenishing_task_info,replenishing_time_per_pod)
        SA.picking_task_manager(Order_Line_selection, Item_pod_Layer, pod_layer_Item,out_stations,column_number, num_lines, static_shelves,unbooked_static_shelves,picking_task_info) #任务货架生成策略，该策略可由客户提供
        print(step,':picking_task_manager')
        CDS.Assign_Tasks_To_AGVs(agv_current_status,picking_task_info,replenishing_task_info,unbooked_static_shelves,static_shelves,agv_current_positions,agv_target_positions,pod_layer_Item,grid_step_time,picking_time_per_item,booked_static_shelves,column_number,moving_shelves,agv_target_pod,pod_status,out_stations,agv_destination_station,agv_seq_no)
        print(step,':Assign_Picking_Tasks_To_AGVs')
        CDS.states_update(agv_current_status,agv_current_positions,agv_target_positions,agv_with_shelves,agv_destination_station,
                  unbooked_static_shelves,booked_static_shelves,moving_shelves,static_shelves,agv_seq_no,vertex_layer_shift,vacant,unbooked_vacant,pod_for_picking_or_replening,node_distance,pod_called_count,pod_called_count_for_replen,
                  out_stations,buffer_list_dic,agv_number,pod_layer_Item,station_picking_tasks,picking_time_per_item,grid_step_time,picking_task_info,agv_target_pod,station_type)
        print(step,':states_update')
        #for agv_seq_no in agv_no_random_list: # 随机选起始agv可能会造成不必要的等待
        for agv_seq_no in range(1, agv_number + 1):
            # 搜路并移动一步
            AGVAGENT.by_dijkstra(agv_target_positions[agv_seq_no - 1],map_current,column_number,row_number,
                              path_incread_weight_per_agv,vertex_layer_shift,agv_paths,agv_paths_weight_sum,occupied_edge_increased_weight,edge_increased_weight,
                              agv_with_shelves,agv_current_positions,agv_current_status,agv_destination_station,buffer_list_dic,agv_seq_no,
                              static_shelves,agv_number,agv_path_segments)
            AGVAGENT.order_path_segments(agv_paths, agv_path_segments,agv_current_positions, agv_seq_no)
            AGVAGENT.Agv_Motion_Model(agv_path_segments, agv_seq_no, agv_kinematic_parameter, agv_motion_state, grid_step_time, agv_current_positions, agv_info_for_map, column_number)

            current_agv_status = agv_current_status[agv_seq_no - 1]
            if current_agv_status == 'shelves have been unloaded' or current_agv_status == 'initial':
                agv_current_status[agv_seq_no - 1] = 'Pod Selection'
            elif current_agv_status == 'to shelves' and (agv_current_positions[agv_seq_no - 1] == agv_target_positions[agv_seq_no - 1]
                    or abs(agv_current_positions[agv_seq_no - 1] - agv_target_positions[agv_seq_no - 1]) == vertex_layer_shift):
                if agv_target_pod[agv_seq_no - 1]==None:
                    agv_current_status[agv_seq_no - 1] = 'to shelves'
                elif agv_target_positions[agv_seq_no - 1]==static_shelves[agv_target_pod[agv_seq_no - 1]]:
                    judgement_result,dislocation_pod_index=AGVAGENT.pod_dislocation_judgement(agv_target_pod[agv_seq_no - 1],map_nodes, static_shelves, column_number)
                    if judgement_result:
                        agv_target_positions[agv_seq_no - 1]=static_shelves[dislocation_pod_index]
                        agv_current_status[agv_seq_no - 1] = 'pod dislocation - to dislocation pod'
                        allowed_move_steps=5 #allowed_move_steps for dislocation pod
                        target_pod_x,target_pod_y=AuxiliaryModule.convert_vertex_to_coordinate(column_number,static_shelves[agv_target_pod[agv_seq_no - 1]])
                        dislocation_pod_x,dislocation_pod_y=AuxiliaryModule.convert_vertex_to_coordinate(column_number,static_shelves[dislocation_pod_index])
                        temporal_station_destination=buffer_list_dic[out_stations[1]][0]
                        pods_for_dislocation[agv_seq_no]=[agv_target_pod[agv_seq_no - 1],dislocation_pod_index,[target_pod_x,target_pod_y],[dislocation_pod_x,dislocation_pod_y],temporal_station_destination,allowed_move_steps] #value is pod index, pod index, pod location, pod location, temporally destination station.
                        pod_status[agv_target_pod[agv_seq_no - 1]]='pod dislocation'
                        pod_status[dislocation_pod_index]='pod dislocation'
                    else:
                        agv_current_status[agv_seq_no - 1] = 'in buffer list selection'
                elif agv_target_pod[agv_seq_no - 1] in pod_status.keys():
                    agv_current_status[agv_seq_no - 1]='to shelves'
                elif agv_target_pod[agv_seq_no - 1] not in pod_status.keys():
                    agv_current_status[agv_seq_no - 1]='to shelves'
                    agv_target_positions[agv_seq_no - 1]=static_shelves[agv_target_pod[agv_seq_no - 1]]
            elif 'pod dislocation' in current_agv_status:
                AGVAGENT.pod_dislocation(agv_current_positions,agv_target_positions,agv_current_status,pods_for_dislocation,static_shelves,pod_status,agv_with_shelves,column_number,agv_seq_no)
            elif current_agv_status == 'to in buffer list of station' and (agv_current_positions[agv_seq_no - 1] == agv_target_positions[agv_seq_no - 1]
                    or abs(agv_current_positions[agv_seq_no - 1] - agv_target_positions[
                agv_seq_no - 1]) == vertex_layer_shift):
                agv_current_status[agv_seq_no - 1] = 'station selection'
            elif agv_current_status[agv_seq_no - 1] == 'to station' and (agv_current_positions[agv_seq_no - 1] == agv_target_positions[agv_seq_no - 1]
                    or abs(agv_current_positions[agv_seq_no - 1] - agv_target_positions[agv_seq_no - 1]) == vertex_layer_shift):
                agv_current_status[agv_seq_no - 1] = 'picking or replenishing items'
            elif agv_current_status[agv_seq_no - 1] == 'picking or replenishing items':
                station_all_picking_info = station_picking_tasks[agv_destination_station[agv_seq_no - 1]] #agv号，货架号，拣货次数
                index_picking_info = [station_all_picking_info.index(x) for x in station_all_picking_info if x[0] == agv_seq_no and x[1] == moving_shelves[agv_seq_no][0]][0]
                if station_picking_tasks[agv_destination_station[agv_seq_no - 1]][index_picking_info][2]<=0.5:
                   agv_current_status[agv_seq_no - 1] = 'out buffer list selection'
                   del station_picking_tasks[agv_destination_station[agv_seq_no - 1]][index_picking_info]
                   AGV_visit_station_count=AGV_visit_station_count+1
                   Average_visit_station_count=AGV_visit_station_count/(step*grid_step_time)
            elif current_agv_status == 'to out buffer list of station' and (agv_current_positions[agv_seq_no - 1] == agv_target_positions[agv_seq_no - 1]
                    or abs(agv_current_positions[agv_seq_no - 1] - agv_target_positions[agv_seq_no - 1]) == vertex_layer_shift):
                if CDS.Assign_tasks_to_station_hopping(moving_shelves,agv_seq_no,picking_task_info,replenishing_task_info,pod_layer_Item,picking_time_per_item,station_type):
                    agv_current_status[agv_seq_no - 1] = 'in buffer list selection'
                else:
                    agv_current_status[agv_seq_no - 1] = 'Pod Storage Selection'
            elif agv_current_status[agv_seq_no - 1] == 'to unoccupied spots by static shelves' and (agv_current_positions[agv_seq_no - 1] == agv_target_positions[agv_seq_no - 1]
                    or abs(agv_current_positions[agv_seq_no - 1] - agv_target_positions[agv_seq_no - 1]) == vertex_layer_shift):
                agv_current_status[agv_seq_no - 1] = 'shelves have been unloaded'

            haveconditions=[]
            if current_agv_status=='Picking Pod Selection':
                status_count=[x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='Picking Pod Selection']
                if not status_count:
                    waiting_counts_in_stations[agv_seq_no]=[['Picking Pod Selection',1]]
                else:
                    status_count=status_count[0]
                    waiting_counts_in_stations[agv_seq_no].remove(status_count)
                    status_count[1]=status_count[1]+1
                    waiting_counts_in_stations[agv_seq_no].append(status_count)
                    haveconditions = [x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='Picking Pod Selection' and x[1] > 20]
            if current_agv_status=='to shelves':
                status_count=[x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='to shelves']
                if not status_count:
                    waiting_counts_in_stations[agv_seq_no]=[['to shelves',1]]
                else:
                    status_count=status_count[0]
                    waiting_counts_in_stations[agv_seq_no].remove(status_count)
                    status_count[1]=status_count[1]+1
                    waiting_counts_in_stations[agv_seq_no].append(status_count)
                    haveconditions = [x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='to shelves' and x[1] > 300]
            if current_agv_status=='out buffer list selection':
                status_count=[x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='out buffer list selection']
                if not status_count:
                    waiting_counts_in_stations[agv_seq_no]=[['out buffer list selection',1]]
                else:
                    status_count=status_count[0]
                    waiting_counts_in_stations[agv_seq_no].remove(status_count)
                    status_count[1]=status_count[1]+1
                    waiting_counts_in_stations[agv_seq_no].append(status_count)
                    haveconditions = [x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='out buffer list selection' and x[1] > 100]
            if current_agv_status=='to out buffer list of out station':
                status_count=[x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='to out buffer list of out station']
                if not status_count:
                    waiting_counts_in_stations[agv_seq_no].append(['to out buffer list of out station',1])
                else:
                    status_count=status_count[0]
                    waiting_counts_in_stations[agv_seq_no].remove(status_count)
                    status_count[1]=status_count[1]+1
                    waiting_counts_in_stations[agv_seq_no].append(status_count)
                    haveconditions = [x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='to out buffer list of out station' and x[1] > 100]
            if current_agv_status=='Pod Storage Selection':
                status_count=[x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='Pod Storage Selection']
                if not status_count:
                    waiting_counts_in_stations[agv_seq_no].append(['Pod Storage Selection',1])
                else:
                    status_count=status_count[0]
                    waiting_counts_in_stations[agv_seq_no].remove(status_count)
                    status_count[1]=status_count[1]+1
                    waiting_counts_in_stations[agv_seq_no].append(status_count)
                    haveconditions = [x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='Pod Storage Selection' and x[1] > 100]
            if current_agv_status=='to unoccupied spots by static shelves':
                status_count=[x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='to unoccupied spots by static shelves']
                if not status_count:
                    waiting_counts_in_stations[agv_seq_no].append(['to unoccupied spots by static shelves',1])
                else:
                    status_count=status_count[0]
                    waiting_counts_in_stations[agv_seq_no].remove(status_count)
                    status_count[1]=status_count[1]+1
                    waiting_counts_in_stations[agv_seq_no].append(status_count)
                    haveconditions = [x for x in waiting_counts_in_stations[agv_seq_no] if x[0]=='Pod Storage Selection' and x[1] > 300]
            if  current_agv_status=='shelves have been unloaded':
                for each_status in waiting_counts_in_stations[agv_seq_no]:
                    each_status[1]=0
            aaaaa=False

            if haveconditions:
                aaaaa=True
            pass
            agv_info_for_map[agv_seq_no - 1][1] = agv_current_status[agv_seq_no - 1]
            other_information['current_agv_status']=agv_current_status[agv_seq_no - 1]
            other_information['current_agv_target_position'] =str(agv_target_positions[agv_seq_no - 1])
            other_information['path']=str(agv_paths[agv_seq_no - 1])
            other_information['AGV_Visit_Count_Per_Second']=str(Average_visit_station_count)

        file_name=result.write_positions_to_file(column_number, agv_info_for_map, static_shelves, other_information,simulation_start_time + grid_step_time * step)
        result.agvshelf("./SnapShots/"+file_name)
#        result.efficient_information(simulation_steps,simulation_progress,simulation_progress_time,
#                              simulation_start_time, step, grid_step_time, waiting_count, agv_number,
#                              finished_package_count, conf, out_station_package_count,
#                              efficient_info)

    result.write_simulation_results_to_file(simulation_total_time,grid_length,agv_number,
                                     finished_package_count,waiting_count,agv_move_step_count,conf,
                                     simulation_start_time,efficient_info,agv_finished_package_count,agv_wait_times)
    result.drawmap_main(boundary_nodes_x,boundary_nodes_y)
main()