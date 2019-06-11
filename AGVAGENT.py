import networkx
import AuxiliaryModule
import copy
import ConfigManager as CM
import numpy
import math


global vertex_layer_shift
vertex_layer_shift = None


#######################################################PathPlanning################################################################################
def by_dijkstra(current_agv_target_vertex,map_current,column_number,row_number,
                              path_incread_weight_per_agv,vertex_layer_shift,agv_paths,agv_paths_weight_sum,occupied_edge_increased_weight,edge_increased_weight,
                              agv_with_shelves,agv_current_positions,agv_current_status,agv_destination_station,buffer_list_dic,agv_seq_no,
                              static_shelves,agv_number,agv_path_segments):
    current_agv_current_vertex=agv_current_positions[agv_seq_no-1]
    if agv_current_status[agv_seq_no-1] not in 'to out buffer list of station' and agv_current_status[agv_seq_no-1] not in 'to station' \
            and agv_current_status[agv_seq_no-1] not in 'picking or replenishing items'and agv_current_status[agv_seq_no-1] not in 'out buffer list selection':
            if current_agv_current_vertex != current_agv_target_vertex:
                # 搜路之前先恢复旧路径对权重的影响
                old_path = agv_paths[agv_seq_no - 1]
                old_path_weight_sum=agv_paths_weight_sum[agv_seq_no - 1]
                AuxiliaryModule.adjust_edge_weight_in_path(map_current, old_path, -path_incread_weight_per_agv)
                path = None
                try:
                    map_current_temp = copy.deepcopy(map_current)
                    MapWeightAdjust(map_current_temp, current_agv_current_vertex, agv_current_positions, agv_number,column_number, row_number,
                                    vertex_layer_shift, occupied_edge_increased_weight,edge_increased_weight,agv_seq_no,agv_path_segments,current_agv_target_vertex)
                    if agv_seq_no not in agv_with_shelves:
                        path = networkx.dijkstra_path(map_current_temp, source=current_agv_current_vertex,
                                                      target=current_agv_target_vertex)  # xiugai
                        pass  # if no exception, means find a path successfully
                    else:  # 处理存疑
 #                       try:
                            vertex_of_static_shelves = sorted(list(static_shelves.values()))
                            for each_vertex in vertex_of_static_shelves:
                                AuxiliaryModule.remove_edges_to_vertex(map_current_temp, column_number, row_number, vertex_layer_shift,
                                                               each_vertex)
                            path = networkx.dijkstra_path(map_current_temp, source=current_agv_current_vertex,
                                                          target=current_agv_target_vertex)  # xiugai
                            pass  # if no exception, means find a path successfully
 #                       except Exception as e:  # path search failed
#                            aaa = [one for one in map_current.nodes()]
#                            aaa = sorted(aaa)
 #                           bbb = [one for one in map_current.edges() if one[0] > vertex_layer_shift]
                            # DrawMap.drawmap_for_path_search(map_current,current_agv_current_vertex, current_agv_target_vertex)
  #                          path = None

                except Exception as e:  # path search failed
                    path = None
                    print('path is none')
        #        new_weight_sum=path_weight_sum(path,map_current_temp)
                agv_paths[agv_seq_no - 1] = path
        #        agv_paths_weight_sum[agv_seq_no - 1] = new_weight_sum
        #        if new_weight_sum is not None and old_path_weight_sum is not None and (old_path[0]==path[0]) and (old_path[-1]==path[-1]):
        #            if old_path_weight_sum<=new_weight_sum:
        #               agv_paths[agv_seq_no - 1] = old_path
        #               agv_paths_weight_sum[agv_seq_no - 1] = old_path_weight_sum
        #        agv_paths[agv_seq_no - 1] = path
                AuxiliaryModule.adjust_edge_weight_in_path(map_current, agv_paths[agv_seq_no - 1], path_incread_weight_per_agv)
    else:
        if agv_current_status[agv_seq_no-1] in 'out buffer list selection' or agv_current_status[agv_seq_no-1] in 'picking or replenishing items':
            agv_paths[agv_seq_no - 1] = None
        else:
            full_path=buffer_list_dic[agv_destination_station[agv_seq_no-1]]
            current_location_index=full_path.index(agv_current_positions[agv_seq_no-1])
            agv_paths[agv_seq_no - 1] = full_path[current_location_index:]


def order_path_segments(agv_paths,agv_path_segments,agv_current_positions,agv_seq_no):
    global vertex_layer_shift
    if vertex_layer_shift is None:
        vertex_layer_shift = CM.get_vertex_layer_shift()
    path=agv_paths[agv_seq_no - 1]
    current_location=agv_current_positions[agv_seq_no - 1]
    if current_location>=vertex_layer_shift:
        current_location=current_location-vertex_layer_shift
    if path is not None:
        initial_path_segment=[]
        for eachelement in path:
            if eachelement>=vertex_layer_shift:
                eachelement=eachelement-vertex_layer_shift
            if eachelement not in initial_path_segment and len(initial_path_segment)<6:
                initial_path_segment.append(eachelement)
            if len(initial_path_segment)>=6:
                break
    else:
        initial_path_segment=path
    del agv_path_segments[agv_seq_no - 1]
    if initial_path_segment is not None and len(initial_path_segment)>=1:
            for i_initial in range(1,len(initial_path_segment)+1):
                for i_agv_segment in range(1,len(agv_path_segments)+1):
                    try:
                       if initial_path_segment[i_initial-1] in agv_path_segments[i_agv_segment-1]:
                            new_path_segment=initial_path_segment[:i_initial-1]
                            agv_path_segments.insert(agv_seq_no - 1, new_path_segment)
                            return
                    except Exception as e:
                        print('error1:%s,%s',i_initial,initial_path_segment)
                        print('error1:%s,%s',i_agv_segment,agv_path_segments)
            agv_path_segments.insert(agv_seq_no - 1, initial_path_segment)
            return
    else:
        agv_path_segments.insert(agv_seq_no - 1,[current_location])

def MapWeightAdjust(map_current_temp, agv_current_vertex,agv_current_positions,agv_number,column_number, row_number, vertex_layer_shift,occupied_edge_increased_weight,edge_increased_weight,agv_seq_no,agv_path_segments,current_agv_target_vertex):
#处于当前agv5米范围内的agv边权值增加
    for i_agv in range(1,agv_number+1):
        agv_vertex=agv_current_positions[i_agv-1]
        if agv_path_segments[agv_seq_no-1] !=None and agv_vertex!=current_agv_target_vertex:
            if len(agv_path_segments[agv_seq_no-1])<=1:
                edge_increased_weight[agv_seq_no - 1]=edge_increased_weight[agv_seq_no-1]*1.1
            else:
                edge_increased_weight[agv_seq_no - 1] = edge_increased_weight[agv_seq_no - 1] /1.05
                if edge_increased_weight[agv_seq_no - 1]<=occupied_edge_increased_weight:
                    edge_increased_weight[agv_seq_no - 1] =occupied_edge_increased_weight
        edge_adjust_weight=edge_increased_weight[agv_seq_no-1]
        if int(abs(agv_vertex-agv_current_vertex)//column_number)<=5 and int(abs(agv_vertex-agv_current_vertex)%column_number)<=5:
            AuxiliaryModule.adjust_edge_weight_to_vertex(map_current_temp, column_number, row_number, vertex_layer_shift,
                                                     agv_vertex, edge_adjust_weight)




def path_weight_sum(current_path,map_current_temp):
    if current_path is None:
        weight_sum = None
    else:
        weight_sum=0
        for i_edge in range(1,len(current_path)):
         weight_sum=map_current_temp.get_edge_data(current_path[i_edge-1], current_path[i_edge])['weight']+weight_sum
    return weight_sum


#######################################################VehicleModel################################################################################

def Agv_Motion_Model(agv_path_segments,agv_seq_no,agv_kinematic_parameter,agv_motion_state,grid_step_time,agv_current_positions,agv_info_for_map,column_number):
    Move_direction=[]
    MaxSpeed=agv_kinematic_parameter[0]
    AcceleratedSpeed=agv_kinematic_parameter[1]
    MaxAngularSpeed=agv_kinematic_parameter[2]
    AngularAcceleration=agv_kinematic_parameter[3]
    first_stop_point,target_orientation=decide_first_stop_point(agv_motion_state,Move_direction,agv_path_segments,column_number,agv_seq_no)
    stop_poin_x,stop_poin_y=AuxiliaryModule.convert_vertex_to_coordinate(column_number,first_stop_point)
    time_left=agv_translation(agv_motion_state[agv_seq_no - 1], stop_poin_x,stop_poin_y,grid_step_time, MaxSpeed, AcceleratedSpeed,column_number)
    agv_rotation(agv_motion_state[agv_seq_no - 1], Move_direction, target_orientation, time_left, MaxAngularSpeed, AngularAcceleration)
    agv_current_positions[agv_seq_no - 1] = AuxiliaryModule.convert_coordinate_to_vertex(column_number,int(round(agv_motion_state[agv_seq_no - 1][0])),int(round(agv_motion_state[agv_seq_no - 1][1])))
    agv_info_for_map[agv_seq_no - 1][0] = agv_current_positions[agv_seq_no - 1]


def velocity_profile(current_speed,distance,MaxSpeed,Acceleration,time_available):
    break_point1=0.5*current_speed*current_speed/Acceleration
    break_point2=(MaxSpeed-current_speed)/Acceleration*0.5*(current_speed+MaxSpeed)+0.5*MaxSpeed/Acceleration*MaxSpeed
    if distance<=break_point1:
        if time_available>(current_speed/Acceleration):
            V=0
            remaining_distance=distance-0.5*current_speed/Acceleration*current_speed
            remaining_time=time_available-current_speed/Acceleration
        else:
            V=current_speed-time_available*Acceleration
            remaining_distance=distance-0.5*(V+current_speed)*time_available
            remaining_time=0
    elif distance<=break_point2 and distance>break_point1:
        VMAX=numpy.sqrt(Acceleration*distance+0.5*current_speed*current_speed)
        if time_available>(((VMAX-current_speed)/Acceleration)+VMAX/Acceleration):
            V=0
            remaining_distance=0
            remaining_time=time_available-((VMAX-current_speed)/Acceleration)-VMAX/Acceleration
        elif (time_available>((VMAX-current_speed)/Acceleration)) and time_available<=(((VMAX-current_speed)/Acceleration)+VMAX/Acceleration):
           V=VMAX-(time_available-(VMAX-current_speed)/Acceleration)*Acceleration
           remaining_distance=0.5*V*V/Acceleration
           remaining_time=0
        else:
            V=current_speed+time_available*Acceleration
            remaining_distance=distance-0.5*(V+current_speed)*time_available
            remaining_time=0
    elif distance>break_point2:
        VMAX=MaxSpeed
        if (time_available<=((VMAX-current_speed)/Acceleration)):
            V=current_speed+time_available*Acceleration
            remaining_distance=distance-0.5*(current_speed+V)*(V-current_speed)/Acceleration
            remaining_time=0
        elif (time_available<((VMAX-current_speed)/Acceleration+(distance-break_point2)/VMAX)) and (time_available>((VMAX-current_speed)/Acceleration)):
            V=VMAX
            remaining_distance=distance-0.5*(current_speed+V)*(V-current_speed)/Acceleration-V*(time_available-(V-current_speed)/Acceleration)
            remaining_time = 0
        elif (time_available>((VMAX-current_speed)/Acceleration+(distance-break_point2)/VMAX)) and (time_available<(VMAX/Acceleration+(VMAX-current_speed)/Acceleration+(distance-break_point2)/VMAX)):
            V=((VMAX/Acceleration+(VMAX-current_speed)/Acceleration+(distance-break_point2)/VMAX)-time_available)*Acceleration
            remaining_distance=0.5*V*V/Acceleration
            remaining_time = 0
        else:
            V = 0
            remaining_distance = 0
            remaining_time=time_available-VMAX/Acceleration-(VMAX-current_speed)/Acceleration-(distance-break_point2)/VMAX
    return V,remaining_distance,remaining_time

def agv_translation(agv_motion_state,stop_poin_x,stop_poin_y,time,MaxSpeed,AcceleratedSpeed,column_number):
    X = agv_motion_state[0]
    Y = agv_motion_state[1]
    Vx = agv_motion_state[2]
    Vy = agv_motion_state[3]
    R = agv_motion_state[4]
#    distance=max(abs(X-stop_poin_x),abs(Y-stop_poin_y))
    if abs(R)<=0.001:
       distance=abs(X-stop_poin_x)
       Vx_,remaining_distance,time_left=velocity_profile(abs(Vx), distance, MaxSpeed, AcceleratedSpeed, time)
       Vx=Vx_
       X=stop_poin_x-remaining_distance
    elif abs(R - 180) <= 0.001:
        distance = abs(X - stop_poin_x)
        Vx_, remaining_distance,time_left = velocity_profile(abs(Vx), distance, MaxSpeed, AcceleratedSpeed, time)
        Vx = -Vx_
        X = stop_poin_x + remaining_distance
    elif  abs(R-90)<=0.001:
        distance = abs(Y - stop_poin_y)
        Vy_, remaining_distance,time_left = velocity_profile(abs(Vy), distance, MaxSpeed, AcceleratedSpeed, time)
        Vy = Vy_
        Y = stop_poin_y - remaining_distance
    elif abs(R - 270) <= 0.001:
        distance = abs(Y - stop_poin_y)
        Vy_, remaining_distance,time_left = velocity_profile(abs(Vy), distance, MaxSpeed, AcceleratedSpeed, time)
        Vy = -Vy_
        Y = stop_poin_y + remaining_distance
    else:
        time_left=time
    agv_motion_state[0]=X
    agv_motion_state[1]=Y
    agv_motion_state[2]=Vx
    agv_motion_state[3]=Vy
    agv_motion_state[4]=R
    return time_left

def agv_rotation(agv_motion_state,Move_direction,target_orientation,time,MaxAngularSpeed, AngularAcceleration):
    R = agv_motion_state[4]
    W= agv_motion_state[5]
    if time>0:
        if R > target_orientation and (R - target_orientation) >= 180:
            W, distance_angular,remaining_time = velocity_profile(W, abs(360 + target_orientation- R), MaxAngularSpeed, AngularAcceleration, time)
            R = 360 + target_orientation - distance_angular
            if R >= 360:
                R = R - 360
        elif R > target_orientation and (R - target_orientation) <= 180:
            W, distance_angular,remaining_time = velocity_profile(W, (R - target_orientation), MaxAngularSpeed, AngularAcceleration,
                                                   time)
            R = target_orientation + distance_angular
        elif R < target_orientation and (target_orientation - R) <= 180:
            W, distance_angular,remaining_time = velocity_profile(W, (target_orientation - R), MaxAngularSpeed, AngularAcceleration,
                                                   time)
            R = target_orientation - distance_angular
        elif R < target_orientation and (target_orientation- R) >= 180:
            W, distance_angular,remaining_time = velocity_profile(W, (360 + R - target_orientation), MaxAngularSpeed,
                                                   AngularAcceleration, time)
            R = target_orientation + distance_angular - 360
            if R <= 0:
                R = R + 360
        if abs(R-target_orientation)<0.0001:
            R=target_orientation
    agv_motion_state[4]=R
    agv_motion_state[5]=W

def decide_first_stop_point(agv_motion_state,Move_direction,agv_path_segments,column_number,agv_seq_no):
    global vertex_layer_shift
    if vertex_layer_shift is None:
        vertex_layer_shift = CM.get_vertex_layer_shift()
    R=agv_motion_state[agv_seq_no - 1][4]
    for i_direction in range(1,len(agv_path_segments[agv_seq_no-1])):
        dif_agv_path_segments=int(agv_path_segments[agv_seq_no-1][i_direction]-agv_path_segments[agv_seq_no-1][i_direction-1])
        Rtarget=0
        if (dif_agv_path_segments)==1:
            Rtarget=0
        elif(dif_agv_path_segments)==-1:
            Rtarget=180
        elif(dif_agv_path_segments)==int(-1*column_number):
            Rtarget=270
        elif(dif_agv_path_segments)==int(column_number):
            Rtarget=90
 #       elif abs(dif_agv_path_segments)==vertex_layer_shift:
 #           Rtarget=1000000
        Move_direction.append(Rtarget)

    lenth_array=len(agv_path_segments[agv_seq_no-1])
    orientation = R
    if lenth_array<1:
        node=None
    else:
        node=agv_path_segments[agv_seq_no-1][lenth_array-1]
    for i in range(1,lenth_array):
        if abs(R-Move_direction[i-1])>0.001 and abs(R-Move_direction[i-1])<50000:
            node=agv_path_segments[agv_seq_no-1][i-1]
            orientation=Move_direction[i-1]
            return node,orientation
    agv_motion_state[agv_seq_no - 1][4]=R
    return node,orientation

###############################################################################pod dislocation######################################################
def pod_dislocation_judgement(pod_index,map_nodes,static_shelves,column_num):
    result=False
    dislocation_pod_index=None
    pod_vertex=static_shelves[pod_index]
    neighbour_vertex=[pod_vertex-column_num,pod_vertex+column_num,pod_vertex-1,pod_vertex+1]
    neighbour_vertex=[x for x in neighbour_vertex if x not in map_nodes or x in static_shelves.values()]
    neighbour_pod_vertex = [x for x in neighbour_vertex if x in static_shelves.values()]
    if len(neighbour_vertex)==4 and neighbour_pod_vertex:
        for each_pod in neighbour_pod_vertex:
            this_pod_neighbour_vertex = [each_pod - column_num, each_pod + column_num, each_pod - 1, each_pod + 1]
            this_pod_neighbour_vertex=[x for x in this_pod_neighbour_vertex if x not in static_shelves.values() and x in map_nodes]
            if this_pod_neighbour_vertex:
                dislocation_pod = each_pod
                dislocation_pod_index=AuxiliaryModule.get_key_by_value(static_shelves,dislocation_pod)[0]
                result=True
                break
    return result,dislocation_pod_index

def pod_dislocation(agv_current_positions,agv_target_positions,agv_current_status,pods_for_dislocation,static_shelves,pod_status,agv_with_shelves,column_number,agv_seq_no):
    agv_status=agv_current_status[agv_seq_no - 1]
    if agv_status=='pod dislocation - to dislocation pod':
        if agv_current_positions[agv_seq_no - 1]!=agv_target_positions[agv_seq_no - 1]:
            pass
        else:
            agv_target_positions[agv_seq_no - 1]=pods_for_dislocation[agv_seq_no][-2]
            del static_shelves[pods_for_dislocation[agv_seq_no][1]]
            agv_with_shelves.append(agv_seq_no)
            agv_current_status[agv_seq_no - 1]='pod dislocation - move dislocation pod'
    elif agv_status== 'pod dislocation - move dislocation pod':
        current_position_x,current_position_y=AuxiliaryModule.convert_vertex_to_coordinate(column_number,agv_current_positions[agv_seq_no - 1])
        travel_distance=abs(current_position_x-pods_for_dislocation[agv_seq_no][3][0])+abs(current_position_y-pods_for_dislocation[agv_seq_no][3][1])
        if travel_distance<pods_for_dislocation[agv_seq_no][-1]:
            pass
        else:
            static_shelves[pods_for_dislocation[agv_seq_no][1]]=agv_current_positions[agv_seq_no - 1]
            agv_target_positions[agv_seq_no - 1] =static_shelves[pods_for_dislocation[agv_seq_no][0]]
            agv_current_status[agv_seq_no - 1] = 'pod dislocation - to target pod'
            agv_with_shelves.remove(agv_seq_no)
    elif agv_status=='pod dislocation - to target pod':
        if agv_current_positions[agv_seq_no - 1]!=agv_target_positions[agv_seq_no - 1]:
            pass
        else:
            agv_target_positions[agv_seq_no - 1] = pods_for_dislocation[agv_seq_no][-2]
            del static_shelves[pods_for_dislocation[agv_seq_no][0]]
            agv_current_status[agv_seq_no - 1] = 'pod dislocation - move target pod'
            agv_with_shelves.append(agv_seq_no)
    elif agv_status== 'pod dislocation - move target pod':
        current_position_x, current_position_y = AuxiliaryModule.convert_vertex_to_coordinate(column_number, agv_current_positions[agv_seq_no - 1])
        travel_distance=abs(current_position_x-pods_for_dislocation[agv_seq_no][2][0])+abs(current_position_y-pods_for_dislocation[agv_seq_no][2][1])
        if travel_distance<(pods_for_dislocation[agv_seq_no][-1]+1):
            pass
        else:
            static_shelves[pods_for_dislocation[agv_seq_no][0]]=agv_current_positions[agv_seq_no - 1]
            agv_target_positions[agv_seq_no - 1]=static_shelves[pods_for_dislocation[agv_seq_no][1]]
            agv_current_status[agv_seq_no - 1] = 'pod dislocation - to dislocation pod a second time'
            agv_with_shelves.remove(agv_seq_no)
    elif agv_status=='pod dislocation - to dislocation pod a second time':
        if agv_current_positions[agv_seq_no - 1]!=agv_target_positions[agv_seq_no - 1]:
            pass
        else:
            agv_target_positions[agv_seq_no - 1] =AuxiliaryModule.convert_coordinate_to_vertex(column_number,pods_for_dislocation[agv_seq_no][2][0],pods_for_dislocation[agv_seq_no][2][1])
            del static_shelves[pods_for_dislocation[agv_seq_no][1]]
            agv_current_status[agv_seq_no - 1] = 'pod dislocation - move dislocation pod to the initial vertex of target pod'
            agv_with_shelves.append(agv_seq_no)
    elif agv_status=='pod dislocation - move dislocation pod to the initial vertex of target pod':
        if agv_current_positions[agv_seq_no - 1]!=agv_target_positions[agv_seq_no - 1]:
            pass
        else:
            static_shelves[pods_for_dislocation[agv_seq_no][1]]=agv_current_positions[agv_seq_no - 1]
            agv_target_positions[agv_seq_no - 1] =static_shelves[pods_for_dislocation[agv_seq_no][0]]
            agv_current_status[agv_seq_no - 1] = 'pod dislocation - to target pod a second time'
            agv_with_shelves.remove(agv_seq_no)
    elif agv_status=='pod dislocation - to target pod a second time':
        if agv_current_positions[agv_seq_no - 1]!=agv_target_positions[agv_seq_no - 1]:
            pass
        else:
            agv_current_status[agv_seq_no - 1]='in buffer list selection'
            del pod_status[pods_for_dislocation[agv_seq_no][0]]
            del pod_status[pods_for_dislocation[agv_seq_no][1]]
            del static_shelves[pods_for_dislocation[agv_seq_no][0]]
            static_shelves[pods_for_dislocation[agv_seq_no][0]]=AuxiliaryModule.convert_coordinate_to_vertex(column_number,pods_for_dislocation[agv_seq_no][3][0],pods_for_dislocation[agv_seq_no][3][1])
            del pods_for_dislocation[agv_seq_no]




