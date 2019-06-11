import math
import graphics
import ConfigManager as CM
import os
import sys
import configparser
import random
###################################################CoordinateConverter###########################################################
global vertex_layer_shift
vertex_layer_shift = None
def convert_vertex_to_coordinate(column_number, vertex):
    global vertex_layer_shift
    if vertex_layer_shift is None:
        vertex_layer_shift = CM.get_vertex_layer_shift()
    if(vertex > vertex_layer_shift):
        vertex = vertex - vertex_layer_shift
        x = (vertex - 1) % column_number
        y = (vertex - 1) // column_number
    else:
        x = (vertex - 1) % column_number
        y = (vertex - 1) // column_number
    return x, y

# print(convert_vertex_to_coordinate(100, 231))


def convert_coordinate_to_vertex(column_number, x, y):
    return int(round(x)) + 1 + int(round(y)) * column_number

# print(convert_coordinate_to_vertex(100, 30, 2))


def get_neighbor_node_left(column_number, row_number, vertex):
    global vertex_layer_shift
    if vertex_layer_shift is None:
        vertex_layer_shift = CM.get_vertex_layer_shift()
    x, y = convert_vertex_to_coordinate(column_number, vertex)
    if (x <= 0):
        return -1
    increase_num = 0
    if vertex > vertex_layer_shift:
        increase_num = vertex_layer_shift
    return convert_coordinate_to_vertex(column_number, x - 1, y) + increase_num

def get_neighbor_node_right(column_number, row_number, vertex):
    global vertex_layer_shift
    if vertex_layer_shift is None:
        vertex_layer_shift = CM.get_vertex_layer_shift()
    x, y = convert_vertex_to_coordinate(column_number, vertex)
    if (x >= column_number - 1):
        return -1
    increase_num = 0
    if vertex > vertex_layer_shift:
        increase_num = vertex_layer_shift
    return convert_coordinate_to_vertex(column_number, x + 1, y) + increase_num

def get_neighbor_node_up(column_number, row_number, vertex):
    global vertex_layer_shift
    if vertex_layer_shift is None:
        vertex_layer_shift = CM.get_vertex_layer_shift()
    x, y = convert_vertex_to_coordinate(column_number, vertex)
    if (y <= 0):
        return -1
    increase_num = 0
    if vertex > vertex_layer_shift:
        increase_num = vertex_layer_shift
    return convert_coordinate_to_vertex(column_number, x, y - 1) + increase_num

def get_neighbor_node_down(column_number, row_number, vertex):
    global vertex_layer_shift
    if vertex_layer_shift is None:
        vertex_layer_shift = CM.get_vertex_layer_shift()
    x, y = convert_vertex_to_coordinate(column_number, vertex)
    if (y >= row_number - 1):
        return -1
    increase_num = 0
    if vertex > vertex_layer_shift:
        increase_num = vertex_layer_shift
    return convert_coordinate_to_vertex(column_number, x, y + 1) + increase_num

def convert_str_coordinates(str):
    str = str[str.index('(') + 1:str.index(')')]
    str_coordinates = str.split(',')
    area_coordinates = []
    for str_element in str_coordinates:
        if len(area_coordinates)<2:
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

def convert_Rectangl_coordinates(str_point,lenth):
    point_coordinates = convert_str_coordinates(str_point)
    if (len(point_coordinates) != 2):
         raise Exception()
    return  graphics.Rectangle(graphics.Point(int(point_coordinates[0])-int(lenth)/2,int(point_coordinates[1])-int(lenth)/2), graphics.Point(int(point_coordinates[0])+int(lenth)/2,int(point_coordinates[1])+int(lenth)/2))


# circ = Circle(p1, 100)

def convert_Circle_coordinates(str_point,lenth):
    point_coordinates = convert_str_coordinates(str_point)
    if (len(point_coordinates) != 2):
         raise Exception()
    return  graphics.Circle(graphics.Point(int(point_coordinates[0]),int(point_coordinates[1])), 1)

def wall_street_distance(column_number,start_vertex,end_vertes):
    start_point_x,start_point_y=convert_vertex_to_coordinate(column_number,start_vertex)
    end_point_x,end_point_y=convert_vertex_to_coordinate(column_number,end_vertes)
    wall_street_distance=abs(start_point_x-end_point_x)+abs(start_point_y-end_point_y)
    return wall_street_distance



########################################################GetFileinfor###########################################################################


def getAllFileName(path):
    lists = os.listdir(path)  # 列出目录的下所有文件和文件夹保存到lists
    lists.sort(key=lambda fn: os.path.getmtime(path + "\\" + fn))  # 按时间排序
    return lists

def getCurFileName(path):
    lists = getAllFileName(path)
    file_new = os.path.join(path, lists[-1])
    return file_new

def getAgvShelfInfoFromFile(filename):
    try:
        current_path = os.getcwd()
        config_reader = configparser.ConfigParser()
        file_path = current_path + "/config.ini"
        config_reader.read(file_path)
        column_number=int(config_reader.get('map', 'column_number'))
        file_path = current_path + filename
        config_reader.read(file_path)
        list = {}

        listindex = -1
        i = 0
        while True:
            try:
                i = i + 1
                agv_info=config_reader.get('agv information', 'agv_' + str(i))
                agv_point_string=str(convert_vertex_to_coordinate(column_number, int(agv_info[agv_info.index('[') + 1:agv_info.index(']')].split(',')[0])))
                substract_area = convert_Rectangl_coordinates(
                    agv_point_string, '1')
                listindex = listindex + 1;
                agv_status= agv_info[agv_info.index('[') + 1:agv_info.index(']')].split(',')[1] # whether this agv has shelf
                if "initial" in agv_status  or  "shelves have been unloaded" in agv_status  or  "to shelves" in agv_status :
                   list[listindex] = {"point": substract_area, "type": "Rectangl_agv", "colour": "black","no":i}
                elif  "shelves have been loaded" in agv_status  or  "to in buffer list of station" in agv_status or "to station" in agv_status\
                        or "in buffer list selection" in agv_status or "station selection" in agv_status or 'picking or replenishing items' in agv_status\
                        or 'pod dislocation - move dislocation pod' in agv_status or 'pod dislocation - move target pod'  in agv_status  or  'pod dislocation - move dislocation pod to the initial vertex of target pod' in agv_status:
                    list[listindex] = {"point": substract_area, "type": "Rectangl_agv", "colour": "red", "no": i}
                elif "to out buffer list of station" in agv_status or "to unoccupied spots by static shelves" in agv_status \
                        or "Pod Storage Selection" in agv_status or "out buffer list selection" in agv_status:
                    list[listindex] = {"point": substract_area, "type": "Rectangl_agv", "colour": "yellow", "no": i}
                else:
                    list[listindex] = {"point": substract_area, "type": "Rectangl_agv", "colour": "black", "no": i}
            except Exception as e:
                #print(e)
                break;

        for each_shelf in config_reader.options('static shelves information'):
            static_shelf_poition=config_reader.get('static shelves information', each_shelf)
            shelf_point_string=str(convert_vertex_to_coordinate(column_number, int(static_shelf_poition)))
            substract_area = convert_Rectangl_coordinates(shelf_point_string, '1')
            listindex = listindex + 1;
            shelf_index=int(each_shelf.split('_')[2])
            list[listindex] = {"point": substract_area, "type": "Rectangl_shelf", "colour": "green","no":shelf_index}

        stime = config_reader.get('simulation', 'time')
        scount=config_reader.get('other information', 'AGV_Visit_Count_Per_Second')

        return list,stime,scount
        # cv2.destroyAllWindows()
    except Exception as e:
        #print(e)
        sys.exit(1)  # fatal error, need exit the program

'''
curfile = getCurFileame("./SnapShots/")
print(curfile)
filelist = getAllFileame("./SnapShots/")
print(filelist)
blist = getAgvInfoFromFile( "/SnapShots/2018-4-10_14-49-20_673.txt")
print(blist)
'''
###################################################MapTool############################################################
# 获取图中到达某点的邻接路径集合
def get_edges_to_vertex(map, column_number, row_number, vertex_layer_shift1, vertex):
    current_layer_vertex = vertex
    if (current_layer_vertex > vertex_layer_shift1):
        second_layer_vertex = current_layer_vertex - vertex_layer_shift1
    else:
        second_layer_vertex = current_layer_vertex + vertex_layer_shift1

    neighbor_edges = []
    count=1
    for i_node in (current_layer_vertex, second_layer_vertex):
       if (current_layer_vertex==second_layer_vertex and count<=1) or (current_layer_vertex!=second_layer_vertex and count<=2):
            current_agv_vertex_left = get_neighbor_node_left(column_number, row_number, i_node)
            current_agv_vertex_right = get_neighbor_node_right(column_number, row_number, i_node)
            current_agv_vertex_up = get_neighbor_node_up(column_number, row_number, i_node)
            current_agv_vertex_down = get_neighbor_node_down(column_number, row_number, i_node)
            if current_agv_vertex_left > 0:
                if (map.has_edge(current_agv_vertex_left, i_node)):
                    edge_1 = {'from_vertex': current_agv_vertex_left, 'to_vertex': i_node}
                    neighbor_edges.append(edge_1)
            if current_agv_vertex_right > 0:
                if (map.has_edge(current_agv_vertex_right, i_node)):
                    edge_1 = {'from_vertex': current_agv_vertex_right, 'to_vertex': i_node}
                    neighbor_edges.append(edge_1)
            if current_agv_vertex_up > 0:
                if (map.has_edge(current_agv_vertex_up, i_node)):
                    edge_1 = {'from_vertex': current_agv_vertex_up, 'to_vertex': i_node}
                    neighbor_edges.append(edge_1)
            if current_agv_vertex_down > 0:
                if (map.has_edge(current_agv_vertex_down, i_node)):
                    edge_1 = {'from_vertex': current_agv_vertex_down, 'to_vertex': i_node}
                    neighbor_edges.append(edge_1)
       count=count+1
    return neighbor_edges

# 移除图中到达某点的邻接路径
def remove_edges_to_vertex(map, column_number, row_number, vertex_layer_shift1, vertex):
    neighbor_edges = get_edges_to_vertex(map, column_number, row_number, vertex_layer_shift1, vertex)
    for edge_1 in neighbor_edges:
        map.remove_edge(edge_1['from_vertex'], edge_1['to_vertex'])
    return


# 根据原始图恢复到达某点的邻接路径
def add_edges_to_vertex(map_original, map, column_number, row_number, vertex_layer_shift1, vertex, weight = 1):
    neighbor_edges = get_edges_to_vertex(map_original, column_number, row_number, vertex_layer_shift1, vertex)
    for edge_1 in neighbor_edges:
        if not map.has_edge(edge_1['from_vertex'], edge_1['to_vertex']):
            map.add_weighted_edges_from([(edge_1['from_vertex'], edge_1['to_vertex'], weight)])
    return


# 根据原始图修改到达某点的邻接路径的权重，相当于先移除再添加新的
def change_edges_to_vertex(map_original, map, column_number, row_number, vertex_layer_shift, vertex, new_weight = 1):
    neighbor_edges = get_edges_to_vertex(map_original, column_number, row_number, vertex_layer_shift, vertex)
    for edge_1 in neighbor_edges:
        if map.has_edge(edge_1['from_vertex'], edge_1['to_vertex']):
            map.remove_edge(edge_1['from_vertex'], edge_1['to_vertex'])
        map.add_weighted_edges_from([(edge_1['from_vertex'], edge_1['to_vertex'], new_weight)])
    return

# 修改邻接路径的权重，在原有的基础上加减权重值
def adjust_edge_weight(map, from_vertex, to_vertex, adjust_weight = 0):
    if map.has_edge(from_vertex, to_vertex):
        current_weight = map.get_edge_data(from_vertex, to_vertex)['weight']
        map.remove_edge(from_vertex, to_vertex)
        map.add_weighted_edges_from([(from_vertex, to_vertex, current_weight + adjust_weight)])
    return

# 修改某条线路上的邻接路径的权重，在原有的基础上加减权重值
def adjust_edge_weight_in_path(map, path, adjust_weight = 0):
    if path is not None and len(path) >= 2:
        for vertex_index in range(0, len(path) - 1):
            adjust_edge_weight(map, path[vertex_index], path[vertex_index + 1], adjust_weight)
    return

# 修改到达某点的邻接路径的权重，在原有的基础上加减权重值
def adjust_edge_weight_to_vertex(map, column_number, row_number, vertex_layer_shift, center_vertex, adjust_weight = 0):
    neighbor_edges = get_edges_to_vertex(map, column_number, row_number, vertex_layer_shift, center_vertex)
    for edge_1 in neighbor_edges:
        adjust_edge_weight(map, edge_1['from_vertex'], edge_1['to_vertex'], adjust_weight)
    return

####################################################other function#####################################################
def get_key_by_value(dict,value):
    return [k for (k,v) in dict.items() if v ==value]

