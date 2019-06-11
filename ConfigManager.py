# -*- coding: UTF-8 -*-
# this module is to load configurations
import configparser
import copy
import os
import sys
import time
import numpy as np
import graphics
import networkx
import result
import AuxiliaryModule


class myexception(Exception):
    def _ini_(self,error):
        self.error=error
    def _str_(self):
        return self.error

global vertex_layer_shift
vertex_layer_shift = None

def get_vertex_layer_shift():
    current_path = os.getcwd()
    config_file_path = current_path + "\config.ini"
    print('loading config file at path: ' + config_file_path)
    config_reader = configparser.ConfigParser()
    config_reader.read(config_file_path)  #
    vertex_layer_shift = int(config_reader.get('map', 'vertex_layer_shift'))
    return vertex_layer_shift

def convert_str_coordinates(str):
    str = str[str.index('(') + 1:str.index(')')]
    str_coordinates = str.split(',')
    area_coordinates = []
    for str_element in str_coordinates:
        area_coordinates.append(int(str_element))
    return str_coordinates


def convert_area_coordinates(str_area):
    area_coordinates = convert_str_coordinates(str_area)
    if (len(area_coordinates) != 4):
         raise Exception()
    return  graphics.Rectangle(graphics.Point(area_coordinates[0],area_coordinates[1]), graphics.Point(area_coordinates[2],area_coordinates[3]))


def convert_point_coordinates(str_point):
    point_coordinates = convert_str_coordinates(str_point)
    if (len(point_coordinates) != 2):
         raise Exception()
    return  graphics.Point(point_coordinates[0], point_coordinates[1])


def read_config_info():
    try:
        current_path = os.getcwd()
        config_file_path = current_path + "\config.ini"
        config_info = open(config_file_path).read()
        return config_info

    except Exception as e:
        print('Error: failed to read configuration file! File path should be at: ' + config_file_path)
        print(e)
        sys.exit(1) # fatal error, need exit the program


def load_config():
    try:
        current_path = os.getcwd()
        config_file_path = current_path + "\config.ini"
        print('loading config file at path: ' + config_file_path)
        config_reader = configparser.ConfigParser()
        config_reader.read(config_file_path) #

        global vertex_layer_shift
        if vertex_layer_shift is None:
            vertex_layer_shift = get_vertex_layer_shift()

        column_number=int(config_reader.get('map', 'column_number'))
        map_grid_length=float(config_reader.get('map', 'grid_length'))
        agv_MaxSpeed=float(config_reader.get('agv', 'MaxSpeed'))
        agv_MaxAngularSpeed = float(config_reader.get('agv', 'MaxAngularSpeed'))
        agv_AngularAcceleration=float(config_reader.get('agv', 'AngularAcceleration'))
        picking_station_num=int(config_reader.get('picking station', 'picking_station_num'))
        replen_station_num = int(config_reader.get('replen station', 'replen_station_num'))
        max_buffer_len_per_in_station = int(config_reader.get('map', 'max_buffer_len_per_in_station'))
        max_buffer_len_per_out_station = int(config_reader.get('map', 'max_buffer_len_per_out_station'))
        representative_picking_station=config_reader.get('picking station', 'representative_picking_station')
        buffer_list_dic={}
        for i_picking_station in range(1,picking_station_num+1):
            if (i_picking_station % 2 == 1):
                i_picking_station_temp=i_picking_station+1
            else:
                i_picking_station_temp=i_picking_station
            picking_station_string=config_reader.get('picking station', 'picking_station_'+str(i_picking_station_temp))
            picking_station = picking_station_string[picking_station_string.index('(') + 1:picking_station_string.index(')')].split(',')
            staion_vertex = AuxiliaryModule.convert_coordinate_to_vertex(column_number, int(picking_station[0]), int(picking_station[1]))
            buffer_list=[]
            for i_buffer_in in range(max_buffer_len_per_in_station,-1,-1):
                buffer_list.append(staion_vertex+column_number*i_buffer_in)
            for i_buffer_out in range(0,max_buffer_len_per_out_station+1,1):
                buffer_list.append(staion_vertex+column_number*i_buffer_out-1)
            if staion_vertex not in buffer_list_dic:
               buffer_list_dic[staion_vertex]=buffer_list
            if (staion_vertex-1) not in buffer_list_dic:
               buffer_list_dic[staion_vertex-1]=buffer_list
        for i_replen_station in range(1,replen_station_num+1):
            replen_station_string = config_reader.get('replen station','replen_station_' + str(i_replen_station))
            replen_station=replen_station_string[replen_station_string.index('(') + 1:replen_station_string.index(')')].split(',')
            station_vertex=AuxiliaryModule.convert_coordinate_to_vertex(column_number, int(replen_station[0]), int(replen_station[1]))
            if (station_vertex-column_number) in buffer_list_dic.keys():
                buffer_list_dic[station_vertex] = buffer_list_dic[station_vertex-column_number]
            else:
                buffer_list_dic[station_vertex] = [station_vertex+1,station_vertex,station_vertex+column_number,station_vertex+column_number+1]





        Translation_weight=map_grid_length/agv_MaxSpeed
        rotation_weight=2*agv_MaxAngularSpeed/agv_AngularAcceleration
        if (90-agv_MaxAngularSpeed/agv_AngularAcceleration*agv_MaxAngularSpeed)>0:
            rotation_weight=rotation_weight+(90-agv_MaxAngularSpeed/agv_AngularAcceleration*agv_MaxAngularSpeed)/agv_MaxAngularSpeed

        map_area = config_reader.get('map', 'initial_area')
        map_coordinates = convert_area_coordinates(map_area)
        map = networkx.DiGraph()
        node_number_col = int(map_coordinates.p2.x - map_coordinates.p1.x + 1)
        node_number_row = int(map_coordinates.p2.y - map_coordinates.p1.y + 1)
        node_number = node_number_col * node_number_row
        map_nodes=[]
        node_distance={}
        boundary_nodes_x={}
        boundary_nodes_y={}
        for i_col in range(1, node_number_col+1):
            for i_row in range(1, node_number_row+1):
                current_node = i_col + node_number_col * (i_row - 1)
                map_nodes.append(current_node)
                second_layer_node = current_node + vertex_layer_shift
                map.add_node(current_node)



                if vertex_layer_shift>0.1:
                   map.add_node(second_layer_node)
                   map.add_weighted_edges_from([(current_node, second_layer_node, rotation_weight)])
                   map.add_weighted_edges_from([(second_layer_node, current_node, rotation_weight)])

                if((i_col % 2 == 1) and (i_row < node_number_row)):
                    neighbor_node_down = current_node + node_number_col
                    map.add_weighted_edges_from([(current_node, neighbor_node_down, Translation_weight)])
                    map.add_weighted_edges_from([(neighbor_node_down,current_node, Translation_weight)])
                if ((i_col % 2 == 0) and (i_row > 1)):
                    neighbor_node_up = current_node - node_number_col
                    map.add_weighted_edges_from([(current_node, neighbor_node_up, Translation_weight)])
                    map.add_weighted_edges_from([(neighbor_node_up,current_node, Translation_weight)])
                if((i_row % 2 == 1) and (i_col > 1)):
                    neighbor_node_left = second_layer_node - 1
                    map.add_weighted_edges_from([(second_layer_node, neighbor_node_left, Translation_weight)])
                    map.add_weighted_edges_from([(neighbor_node_left,second_layer_node, Translation_weight)])
                if ((i_row % 2 == 0) and (i_col < node_number_col)):
                    neighbor_node_right = second_layer_node + 1
                    map.add_weighted_edges_from([(second_layer_node, neighbor_node_right, Translation_weight)])
                    map.add_weighted_edges_from([(neighbor_node_right,second_layer_node, Translation_weight)])

        except_area_num = int(config_reader.get('map', 'substract_area_num'))

        for i_area in range(1,except_area_num+1):
            except_area = config_reader.get('map', 'substract_area_'+str(i_area))
            except_coordiantes = convert_area_coordinates(except_area)

            ex_num_clo_start = int(except_coordiantes.p1.x)+1
            ex_num_clo_end  = int(except_coordiantes.p2.x)+1
            ex_num_row_start = int(except_coordiantes.p1.y)+1
            ex_num_row_end = int(except_coordiantes.p2.y)+1

            for ex_col in range(ex_num_clo_start, ex_num_clo_end+1):
                for ex_row in range(ex_num_row_start, ex_num_row_end + 1):
                    ex_node = ex_col + node_number_col * (ex_row - 1)
                    map.remove_node(ex_node)
                    map_nodes.remove(ex_node)
                    if vertex_layer_shift>0.1:
                        map.remove_node(ex_node + vertex_layer_shift)
        picking_station_except_edge= get_station_except_edge(column_number)
 #       for edge_except_key in picking_station_except_edge.keys():
 #           start_point=picking_station_except_edge[edge_except_key][0]+ vertex_layer_shift
 #           end_point=picking_station_except_edge[edge_except_key][1]+ vertex_layer_shift
 #           if (map.has_edge(start_point,end_point)):
 #               map.remove_edge(start_point,end_point)
        First_node_buffer_list=[]
        for buffer_list_key in buffer_list_dic.keys():
            first_node=buffer_list_dic[buffer_list_key][0]
            end_node=buffer_list_dic[buffer_list_key][-1]
            if first_node not in First_node_buffer_list:
                First_node_buffer_list.append(first_node)
                node_list=buffer_list_dic[buffer_list_key][1:-1]
                for each_node in node_list:
                    map.remove_node(each_node)
                    map.remove_node(each_node+vertex_layer_shift)
                if buffer_list_key<column_number: #只对拣货站做处理
                   map.remove_edge(end_node+vertex_layer_shift, end_node+vertex_layer_shift-1)
                   map.remove_edge(end_node+vertex_layer_shift, end_node+vertex_layer_shift+1)
#        result.drawmap_for_path_search(map,2,7)
#        neighbors = [n for n in map.neighbors(10)]
        print('node_count_total_without_except_area =' + str(map.number_of_nodes()))
        print('edges_count_total_without_except_area =' + str(map.number_of_edges()))
        #print('vertex=',map.nodes)
        station_point=[int(x) for x in convert_str_coordinates(representative_picking_station)]
        for i_node in map_nodes:
            current_node_x, current_node_y = AuxiliaryModule.convert_vertex_to_coordinate(column_number, i_node)
            distance=abs(current_node_x-station_point[0])+abs(current_node_y-station_point[1])
            node_distance[i_node]=[distance]
        get_boundary_nodes(node_number_col,node_number_row,map_nodes,boundary_nodes_x,boundary_nodes_y,picking_station_except_edge)
        map_nodes.sort()
        return map,map_nodes,node_distance,buffer_list_dic,boundary_nodes_x,boundary_nodes_y

    except Exception as e:
        print('Error: failed to read configuration file! File path should be at: ' + config_file_path)
        print(e)
        sys.exit(1) # fatal error, need exit the program

class ConfigPara(object):
    grid_length = 0.7
    agv_num = 10
    agv_speed = 1.5
    column_number =0
    row_number = 0
    #cost_of_turn_around = 0.0
    cost_of_put_package = 1.0
    cost_of_drop_package = 1.0
    simulation_time = 0
    in_station = []
    pod_called_count={}
    pod_called_count_for_replen={}
    out_station = []
    replen_stations=[]
    max_buffer_len_per_in_station = 1
    max_buffer_len_per_out_station =1
    in_station_buffer=[]
    out_station_buffer = []
    unoccupied_vertex=[]
    agv_kinematic=[]
    initial_static_shelves_vertex={}
    Initial_Item_Layer={}
    Initial_Layer_Item={}
    Initial_Order_selection=[]
    charge_efficient=1.0
    num_lines=0
    picking_time_per_item=0
    replenishing_time_per_pod=0
    call_interval_by_replen_station=0
    def LoadConfigFromFile(self,map_nodes,buffer_list_dic):
        try:
            current_path = os.getcwd()
            config_file_path = current_path + "/config.ini"
            print('loading config file at path: ' + config_file_path)
            config_reader = configparser.ConfigParser()
            config_reader.read(config_file_path)

            self.agv_num = int(config_reader.get('agv', 'number'))
            self.agv_maxspeed = float(config_reader.get('agv', 'MaxSpeed'))
            self.grid_length = float(config_reader.get('map', 'grid_length'))
            self.column_number = int(config_reader.get('map', 'column_number'))
            self.row_number = int(config_reader.get('map', 'row_number'))
 #           #self.cost_of_turn_around = float(config_reader.get('agv','cost_of_turn_around'))
            self.cost_of_put_package = float(config_reader.get('agv','cost_of_put_package'))
            self.cost_of_drop_package = float(config_reader.get('agv', 'cost_of_drop_package'))
            self.simulation_time = int(config_reader.get('agv', 'simulation_time'))
            self.max_buffer_len_per_in_station = int(config_reader.get('map', 'max_buffer_len_per_in_station'))
            self.max_buffer_len_per_out_station = int(config_reader.get('map', 'max_buffer_len_per_out_station'))
            self.charge_efficient = float(config_reader.get('agv', 'charge_efficient'))
            self.num_lines= int(config_reader.get('order', 'Num_of_lines_per_order'))
            self.unoccupied_vertex=copy.deepcopy(map_nodes)
            self.agv_kinematic.append(float(config_reader.get('agv', 'MaxSpeed')))
            self.agv_kinematic.append(float(config_reader.get('agv', 'AcceleratedSpeed')))
            self.agv_kinematic.append(float(config_reader.get('agv', 'MaxAngularSpeed')))
            self.agv_kinematic.append(float(config_reader.get('agv', 'AngularAcceleration')))
            NumItemForOneLayer=int(config_reader.get('pod', 'NumItemForOneLayer'))
            NumLayers=int(config_reader.get('pod', 'Layers'))
            pod_num = int(config_reader.get('pod', 'pod_num'))
            item_num=int(config_reader.get('item: Min,Max,Avg,Dev,order possibility,num of layers', 'item_num'))
            self.picking_time_per_item=int(config_reader.get('picking station', 'picking_time_per_item'))
            self.replenishing_time_per_pod=int(config_reader.get('replen station', 'replenishing_time_per_pod'))
            self.call_interval_by_replen_station=int(config_reader.get('replen station', 'call_interval_by_replen_station'))

            PodFullyFilled=[]
            PodStatusOfItem=[]
            DetailedPodStatusOfItem=[]
            for i_layer in range(1,NumLayers+1):
                PodStatusOfItem.append(0) #this means all layers in a pod is empty
                DetailedPodStatusOfItem.append([i_layer,'item',0]) #layer is empty wihout item
            for i_pod in range(1,pod_num+1):
                PodStatusOfItem.append(i_pod)
                PodStatusOfItemTemp=copy.deepcopy(PodStatusOfItem)
                PodFullyFilled.append(PodStatusOfItemTemp) #this means all layers in pod i is empty
                PodStatusOfItem.remove(i_pod)
                DetailedPodStatusOfItemTemp=copy.deepcopy(DetailedPodStatusOfItem)
                self.Initial_Layer_Item[i_pod]=DetailedPodStatusOfItemTemp
                station_coordinates = config_reader.get('pod', 'pod_'+str(i_pod))
                point = convert_point_coordinates(station_coordinates)
                station_vertex = AuxiliaryModule.convert_coordinate_to_vertex(self.column_number,point.x,point.y) # + vertex_layer_shift
                self.unoccupied_vertex.remove(station_vertex)
                self.in_station.append(point)
                self.initial_static_shelves_vertex[i_pod]=station_vertex
                self.pod_called_count[i_pod]=0
                self.pod_called_count_for_replen[i_pod]=0
                buffer_list=[]
                next_vertex = station_vertex
                buffer_list.append(next_vertex)
                for buffer_index in range(1, self.max_buffer_len_per_in_station + 1):
                    next_vertex = AuxiliaryModule.get_neighbor_node_down(self.column_number, self.row_number, next_vertex)
                    buffer_list.append(next_vertex)
                self.in_station_buffer.append(buffer_list)
            picking_station_num = int(config_reader.get('picking station', 'picking_station_num'))
            First_node_buffer_list = []
            for i_out in range(1,picking_station_num+1):
                station_coordinates = config_reader.get('picking station', 'picking_station_' + str(i_out))
                point = convert_point_coordinates(station_coordinates)
                station_vertex = AuxiliaryModule.convert_coordinate_to_vertex(self.column_number,point.x,point.y) # + vertex_layer_shift
                first_node = buffer_list_dic[station_vertex][0]
                if first_node not in First_node_buffer_list:
                    First_node_buffer_list.append(first_node)
                    for each_node in buffer_list_dic[station_vertex]:
                        self.unoccupied_vertex.remove(each_node)
                self.out_station.append(station_vertex)
                buffer_list = []
                next_vertex = station_vertex
                buffer_list.append(next_vertex)
                for buffer_index in range(1, self.max_buffer_len_per_out_station + 1):
                    if int(round(point.x))==0:
                        next_vertex = AuxiliaryModule.get_neighbor_node_right(self.column_number, self.row_number, next_vertex)
                    elif int(round(point.y))==0:
                        next_vertex = AuxiliaryModule.get_neighbor_node_down(self.column_number, self.row_number, next_vertex)
                    buffer_list.append(next_vertex)
                self.out_station_buffer.append(buffer_list)
                replenishing_station_num = int(config_reader.get('replen station', 'replen_station_num'))
            for i_replen in range(1,replenishing_station_num+1):
                station_coordinates = config_reader.get('replen station', 'replen_station_' + str(i_replen))
                point = convert_point_coordinates(station_coordinates)
                station_vertex = AuxiliaryModule.convert_coordinate_to_vertex(self.column_number,point.x,point.y) # + vertex_layer_shift
                self.replen_stations.append(station_vertex)
            for i_item in range(1,item_num+1):
                item_info_string=config_reader.get('item: Min,Max,Avg,Dev,order possibility,num of layers', 'item_'+str(i_item))
                item_info_list = item_info_string[item_info_string.index('(') + 1:item_info_string.index(')')].split(',')
                Item_Layer_info=[]
                MinItemsForOneLine=int(item_info_list[0])
                MaxItemsForOneLine=int(item_info_list[1])
                AvgItemsForOneLine=int(item_info_list[2])
                DevItemsForOneLine=float(item_info_list[3])
                OrderPossibility=float(item_info_list[4])
                NumOfLayers=int(item_info_list[5])
                self.Initial_Order_selection.append(OrderPossibility)
                Item_Layer_info.append([MinItemsForOneLine, MaxItemsForOneLine, AvgItemsForOneLine, DevItemsForOneLine])
                self.Initial_Item_Layer['item_'+str(i_item)]=Item_Layer_info
                for i_item_layer in range(1,NumOfLayers+1):
                    item_filled=False
                    while item_filled==False:
                        fakepod=np.random.randint(1,len(PodFullyFilled)+1)
                        if 0 in PodFullyFilled[fakepod-1]:
                            LayerNum=int(PodFullyFilled[fakepod-1].index(0))
                            pod=int(PodFullyFilled[fakepod-1][NumLayers])
                            PodFullyFilled[fakepod - 1][LayerNum]=1
                            self.Initial_Layer_Item[pod][LayerNum]=[LayerNum+1,'item_'+str(i_item),NumItemForOneLayer]
                            Item_Layer_info.append([pod, LayerNum+1, NumItemForOneLayer])
                            self.Initial_Item_Layer['item_' + str(i_item)]=Item_Layer_info
                            item_filled = True
                        else:
                            del PodFullyFilled[fakepod-1]

        except Exception as e:
            print('Error: failed to read configuration file! File path should be at: ' + config_file_path)
            print(e)
            sys.exit(1)  # fatal error, need exit the program
    def Print(self):
        print('******************************************')
        print('grid_length='+str(self.grid_length))
        print('column_number='+str(self.column_number))
        print('row_number=' + str(self.row_number))
        print('agv_num=' + str(self.agv_num))
#        print('agv_speed=' + str(self.agv_speed))
        print('******************************************')

    def get_in_station_no_by_vertex(self, input_vertex):
        global vertex_layer_shift
        if vertex_layer_shift is None:
            vertex_layer_shift = get_vertex_layer_shift()
        for find_station_no in range(1, len(self.in_station) + 1):
            difference = self.in_station_buffer[find_station_no - 1][0] - input_vertex
            if (difference ==0 or abs(difference) == vertex_layer_shift):
                return find_station_no
        return -1

    def get_in_station_no_by_buffer_vertex(self, input_vertex):
        global vertex_layer_shift
        if vertex_layer_shift is None:
            vertex_layer_shift = get_vertex_layer_shift()
        for find_station_no in range(1, len(self.in_station) + 1):
            buffer_list = self.in_station_buffer[find_station_no - 1]
            for buffer_index in range(0, len(buffer_list)):
                difference = self.in_station_buffer[find_station_no - 1][buffer_index] - input_vertex
                if (difference ==0 or abs(difference) == vertex_layer_shift):
                    return find_station_no
        return -1


def IsvertexOccupy(agv_current_positions,vext):
    second_vertex=0
    global vertex_layer_shift
    if vertex_layer_shift is None:
        vertex_layer_shift = get_vertex_layer_shift()
    if vext > vertex_layer_shift:
        second_vertex = vext - vertex_layer_shift
    else:
        second_vertex = vext + vertex_layer_shift

    point_occupy = True
    try:
        agv_current_positions.index(vext)
    except Exception as e:
        point_occupy = False

    if point_occupy == False:
        try:
            agv_current_positions.index(second_vertex)
            point_occupy = True
        except Exception as e:
            point_occupy = False
    return point_occupy

def IsAgvInDesBuffer(agv_cur,agv_dest,buffer_list,buffer_len):
    global vertex_layer_shift
    if vertex_layer_shift is None:
        vertex_layer_shift = get_vertex_layer_shift()
    for buffer in buffer_list:
        if (buffer[0] == agv_dest):
            for buffer_index in range(1, buffer_len + 1):
                if(buffer[buffer_index] == agv_cur or abs(agv_cur - buffer[buffer_index])==vertex_layer_shift):
                    return True
    return False

def get_boundary_nodes(node_number_col,node_number_row,map_nodes,boundary_x,boundary_y,station_except_edge):
    for i_col in range(1, node_number_col + 1):
        Min_node_found = False
        boudary_nodes_x=[]
        previous_node_status=0
        for i_row in range(1, node_number_row + 1):
            current_node =i_col + node_number_col * (i_row - 1)
            if current_node in map_nodes:
                current_node_status=1
            else:
                current_node_status=0
            if Min_node_found == False:
                if current_node_status!=previous_node_status:
                    Min_node_found = True
                    Min_node = copy.deepcopy(current_node)
                    boudary_nodes_x.append(Min_node)
                    previous_node = current_node
                    previous_node_status = current_node_status
            else:
                if current_node_status!=previous_node_status:
                    if current_node_status==1:
                        boudary_nodes_x.append(current_node)
                    else:
                        boudary_nodes_x.append(previous_node)
                else:
                    if  (i_row==node_number_row) and current_node_status==1:
                        boudary_nodes_x.append(current_node)
                previous_node = current_node
                previous_node_status = current_node_status
            if (i_row==node_number_row) and len(boudary_nodes_x)>1:
                boundary_x[Min_node]=boudary_nodes_x
    for i_row in range(1, node_number_row + 1):
        Min_node_found = False
        boudary_nodes_y=[]
        previous_node_status=0
        for i_col in range(1, node_number_col + 1):
            current_node = i_col + node_number_col * (i_row - 1)
            if current_node in map_nodes:
                current_node_status=1
            else:
                current_node_status=0
            if Min_node_found == False:
                if current_node_status!=previous_node_status:
                    Min_node_found = True
                    Min_node = copy.deepcopy(current_node)
                    boudary_nodes_y.append(Min_node)
                    previous_node = current_node
                    previous_node_status = current_node_status
            else:
                if current_node_status!=previous_node_status:
                    if current_node_status==1:
                        boudary_nodes_y.append(current_node)
                    else:
                        boudary_nodes_y.append(previous_node)
                else:
                    if current_node_status==1 and current_node in station_except_edge:
                        boudary_nodes_y.append(current_node)
                    if  (i_col==node_number_col) and current_node_status==1:
                        boudary_nodes_y.append(current_node)
                previous_node = current_node
                previous_node_status = current_node_status
            if (i_col==node_number_col) and len(boudary_nodes_y)>1:
                boundary_y[Min_node]=boudary_nodes_y

    return boundary_x,boundary_y

def get_station_except_edge(column_num):
    station_except_edge={}
    current_path = os.getcwd()
    config_file_path = current_path + "\config.ini"
    print('loading config file at path: ' + config_file_path)
    config_reader = configparser.ConfigParser()
    config_reader.read(config_file_path)  #
    picking_station_except_edge_num = int(config_reader.get('picking station', 'picking_station_except_edge_num'))
    for i_picking_station_except in range(1, picking_station_except_edge_num + 1):
        except_station_edge_string = config_reader.get('picking station','picking_station_except_edge_' + str(i_picking_station_except))
        except_station_edge=except_station_edge_string[except_station_edge_string.index('(') + 1:except_station_edge_string.index(')')].split(',')
        start_staion=config_reader.get('picking station', except_station_edge[0])
        start_staion_vertex=AuxiliaryModule.convert_coordinate_to_vertex(column_num,int(start_staion[start_staion.index('(') + 1:start_staion.index(')')].split(',')[0]),int(start_staion[start_staion.index('(') + 1:start_staion.index(')')].split(',')[1]))
        end_staion = config_reader.get('picking station', except_station_edge[1])
        end_staion_vertex=AuxiliaryModule.convert_coordinate_to_vertex(column_num,int(end_staion[end_staion.index('(') + 1:end_staion.index(')')].split(',')[0]),int(end_staion[end_staion.index('(') + 1:end_staion.index(')')].split(',')[1]))
        station_except_edge[start_staion_vertex]=[start_staion_vertex,end_staion_vertex]
        station_except_edge[end_staion_vertex] = [end_staion_vertex,start_staion_vertex]
    return station_except_edge