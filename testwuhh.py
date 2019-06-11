import numpy as np
import os
import sys
import configparser
import AuxiliaryModule
import networkx
import pylab
import matplotlib.pyplot as plt
import bisect
import  networkx as nx
import random
#help(networkx.dijkstra_path)
#aaa=AuxiliaryModule.convert_coordinate_to_vertex(72,int(round(37.3125)),int(round(14)))
aaa={}
ddd=[[1,2,3],[4]]
random_num = random.uniform(0.5, 1)
print(random_num)

def test_for_weighted_graphic():
    # 自定义网络
    row = np.array([0, 0, 0, 1, 2, 3, 6])
    col = np.array([1, 2, 3, 4, 5, 6, 7])
    value = np.array([1, 2, 1, 8, 1, 3, 5])

    print('生成一个空的有向图')
    G = nx.DiGraph()
    print('为这个网络添加节点...')
    for i in range(0, np.size(col) + 1):
        G.add_node(i)
    print('在网络中添加带权重的边...')
    for i in range(np.size(row)):
        G.add_weighted_edges_from([(row[i], col[i], value[i])])

    print('给网路设置布局...')
    pos = nx.shell_layout(G)
    print('画出网络图像：')
    nx.draw(G, pos, with_labels=True, node_color='white', edge_color='red', node_size=400, alpha=0.5)
    # pylab.title('Self_Define Net',fontsize=15)
    pylab.show()

    '''
    Shortest Path with dijkstra_path
    '''
    print('dijkstra方法寻找最短路径：')
    path = nx.dijkstra_path(G, source=0, target=7)
    print('节点0到7的路径：', path)
    print('dijkstra方法寻找最短距离：')
    distance = nx.dijkstra_path_length(G, source=0, target=7)
    print('节点0到7的距离为：', distance)


def Create_out_station():
    try:
        current_path = os.getcwd()
        config_file_path = current_path + "\config.ini"
        print('loading config file at path: ' + config_file_path)
        config_reader = configparser.ConfigParser()
        config_reader.read(config_file_path)

        map_area = config_reader.get('map', 'initial_area')
        map_coordinates = AuxiliaryModule.convert_area_coordinates(map_area)
        map = networkx.DiGraph()
        node_number_col = int(map_coordinates.p2.x - map_coordinates.p1.x + 1)
        node_number_row = int(map_coordinates.p2.y - map_coordinates.p1.y + 1)
        node_number = node_number_col * node_number_row

        for i_col in range(1, node_number_col + 1):
            for i_row in range(1, node_number_row + 1):
                current_node = i_col + node_number_col * (i_row - 1)
                map.add_node(current_node)

                if ((i_col > 1)):
                    neighbor_node_left = current_node - 1
                    map.add_weighted_edges_from([(neighbor_node_left, current_node, 1)])
                    map.add_weighted_edges_from([(current_node, neighbor_node_left, 1)])
                if ((i_row > 1)):
                    neighbor_node_up = current_node - node_number_col
                    map.add_weighted_edges_from([(neighbor_node_up, current_node, 1)])
                    map.add_weighted_edges_from([(current_node, neighbor_node_up, 1)])
                if ((i_col < node_number_col)):
                    neighbor_node_right = current_node + 1
                    map.add_weighted_edges_from([(neighbor_node_right, current_node, 1)])
                    map.add_weighted_edges_from([(current_node, neighbor_node_right, 1)])
                if ((i_row < node_number_row)):
                    neighbor_node_down = current_node + node_number_col
                    map.add_weighted_edges_from([(neighbor_node_down, current_node, 1)])
                    map.add_weighted_edges_from([(current_node, neighbor_node_down, 1)])

        except_area_num = int(config_reader.get('map', 'substract_area_num'))
        for i_area in range(1, except_area_num + 1):
            except_area = config_reader.get('map', 'substract_area_' + str(i_area))
            except_coordiantes = AuxiliaryModule.convert_area_coordinates(except_area)

            ex_num_clo_start = int(except_coordiantes.p1.x) + 1
            ex_num_clo_end = int(except_coordiantes.p2.x) + 1
            ex_num_row_start = int(except_coordiantes.p1.y) + 1
            ex_num_row_end = int(except_coordiantes.p2.y) + 1

            for ex_col in range(ex_num_clo_start, ex_num_clo_end + 1):
                for ex_row in range(ex_num_row_start, ex_num_row_end + 1):
                    ex_node = ex_col + node_number_col * (ex_row - 1)
                    map.remove_node(ex_node)
        pos = []
        pos.append((-1, -1))
        for i_row in range(1, node_number_row + 1):
            for i_col in range(1, node_number_col + 1):
                pos.append((i_col, i_row))

        networkx.draw(map, pos, node_color='blue', edge_color='red', node_size=10, alpha=1)  # 按参数构图
        plt.xlim(0, node_number_col + 1)  # 设置首界面X轴坐标范围
        plt.ylim(0, node_number_row + 1)  # 设置首界面Y轴坐标范围
        plt.savefig("out_station.png")
        # plt.show()

        file_path = current_path + '\out_station.txt'
        out_file = configparser.ConfigParser()
        out_file.add_section('out_station')
        node_index = 1
        for i_col in range(1, node_number_col + 1):
            for i_row in range(1, node_number_row + 1):
                current_node = i_col + node_number_col * (i_row - 1)

                if (map.has_node(current_node) == False):
                    continue

                x, y = AuxiliaryModule.convert_vertex_to_coordinate(node_number_col, current_node)

                # if(x == 11 and y >= 21 and y <= 37):
                #     continue
                # if (y == 20 and x <= 11):
                #     continue
                # if (y == 38 and x <= 11):
                #     continue
                if (y <= 1):
                    continue

                left_node = current_node - 1
                down_node = current_node + node_number_col
                right_node = current_node + 1
                up_node = current_node - node_number_col
                if (map.has_edge(current_node, left_node) == False):
                    # x, y = CoordinateConverter.convert_vertex_to_coordinate(node_number_col, current_node)
                    out_file.set('out_station', 'out_station_' + str(node_index), '(' + str(x) + ',' + str(y) + ')')
                    node_index = node_index + 1
                    continue
                if (map.has_edge(current_node, down_node) == False):
                    # x, y = CoordinateConverter.convert_vertex_to_coordinate(node_number_col, current_node)
                    out_file.set('out_station', 'out_station_' + str(node_index), '(' + str(x) + ',' + str(y) + ')')
                    node_index = node_index + 1
                    continue
                if (map.has_edge(current_node, right_node) == False):
                    # x, y = CoordinateConverter.convert_vertex_to_coordinate(node_number_col, current_node)
                    out_file.set('out_station', 'out_station_' + str(node_index), '(' + str(x) + ',' + str(y) + ')')
                    node_index = node_index + 1
                    continue
                if (map.has_edge(current_node, up_node) == False):
                    # x, y = CoordinateConverter.convert_vertex_to_coordinate(node_number_col, current_node)
                    out_file.set('out_station', 'out_station_' + str(node_index), '(' + str(x) + ',' + str(y) + ')')
                    node_index = node_index + 1
                    continue

        with open(file_path, 'w') as fw:
            out_file.write(fw)
    except Exception as e:
        print(e)
        sys.exit(1)  # fatal error, need exit the program


def wuhh1(k):
    return k+1