import os
import sys
import configparser
import networkx
import graphics
import pylab
import AuxiliaryModule
import cv2
import numpy as np
from threading import Timer
import time
global win
import copy
import ConfigManager


####################################################result analysis by draw maps########################################################


colourMap = {
    "white":(255, 255, 255),
    "black":(0,0,0),
    "red":(0,0,255),
    "blue":(255,0,0),
    "green":(0,255,0),
    "pink": (255, 0, 255),
    "yellow": (50, 194, 241),
}

global vertex_layer_shift
vertex_layer_shift = None
global backgroundimg
global k
k = 15
k_shift_x = 40
k_shift_y = 40
k_text = 0.5
map_padding_x = 40
map_padding_y = 80
chosen_font = cv2.QT_FONT_NORMAL



def background(boundary_nodes_x,boundary_nodes_y):
    try:
        current_path = os.getcwd()
        file_path = current_path + "/config.ini"
        config_reader = configparser.ConfigParser()
        config_reader.read(file_path)
#        print('read configuration file: ' + file_path)

        map_area = AuxiliaryModule.convert_area_coordinates(config_reader.get('map', 'initial_area'))

        list = {}
        map_area.setFill("white")
        listindex = 0
        list[listindex] = {"point":map_area,"type":"Rectangl","colour":"white","no":0}
 #       i = 0
 #       while True:
 #           try:
 #               i = i + 1
 #               substract_area = CoordinateConverter.convert_area_coordinates(
 #                   config_reader.get('map', 'substract_area_' + str(i)))
 #               substract_area.setFill("black")
 #               listindex = listindex + 1
 #               list[listindex] = {"point":substract_area,"type":"Rectangl","colour":"black","no":i}
 #           except Exception as e:
 #               #print(e)
 #               break

#        i = 0
#        while True:
#            try:
#                i = i + 1
#                substract_area = CoordinateConverter.convert_Rectangl_coordinates(
#                    config_reader.get('package_in_station', 'in_station_' + str(i)), '1')
#                substract_area.setFill("green")
#                listindex = listindex + 1
                #list[listindex] = substract_area
#                list[listindex] = {"point": substract_area, "type": "Rectangl", "colour": "green","no":i}
#            except Exception as e:
                #print(e)
#                break

        i = 0
        while True:
            try:
                i = i + 1
                substract_area = AuxiliaryModule.convert_Rectangl_coordinates(
                    config_reader.get('picking station', 'picking_station_' + str(i)), '1')
                substract_area.setFill("blue")
                listindex = listindex + 1
                #list[listindex] = substract_area
                list[listindex] = {"point": substract_area, "type": "Rectangl", "colour": "blue","no":i}
            except Exception as e:
                #print(e)
                break

        i=0
        while True:
            try:
                i = i + 1
                substract_area = AuxiliaryModule.convert_Rectangl_coordinates(
                    config_reader.get('replen station', 'replen_station_' + str(i)), '1')
                substract_area.setFill("pink")
                listindex = listindex + 1
                #list[listindex] = substract_area
                list[listindex] = {"point": substract_area, "type": "Rectangl", "colour": "pink","no":i}
            except Exception as e:
                #print(e)
                break


        for index in range(len(list)):
            list[index]["point"].p1.x = list[index]["point"].p1.x * k + k_shift_x
            list[index]["point"].p1.y = list[index]["point"].p1.y * k + k_shift_y
            list[index]["point"].p2.x = list[index]["point"].p2.x * k + k_shift_x
            list[index]["point"].p2.y = list[index]["point"].p2.y * k + k_shift_y

        #print(list)
        #cvmat = cv2.Mat(list[0].p2.y, list[index].p2.x, cv2.CV_8U)
        #cv2.imshow('frame',cvmat)
        griddingPoint=  list[0]["point"]
        img = np.zeros((int(griddingPoint.p2.y) + map_padding_y, int(griddingPoint.p2.x) + map_padding_x, 3), np.uint8)
        # fill the image with white
        img.fill(255)

        node_number_col_map=int(config_reader.get('map', 'column_number'))
        node_number_row_map=int(config_reader.get('map', 'row_number'))
        count = 0
        for i_col in range(1, node_number_col_map+1):
            count = count + 1
            if (count%2) == 0:
                lineclour = colourMap["black"]
            else:
                lineclour = colourMap["yellow"]
            for i_row in range(1, node_number_row_map+1):
                current_node = i_col + node_number_col_map * (i_row - 1)
                if current_node in boundary_nodes_x:
                    Node_array=boundary_nodes_x[current_node]
                    for i_node in range(1,len(Node_array),2):
                         min_node_x,min_node_y=AuxiliaryModule.convert_vertex_to_coordinate(node_number_col_map,Node_array[i_node-1])
                         max_node_x,max_node_y=AuxiliaryModule.convert_vertex_to_coordinate(node_number_col_map,Node_array[i_node])
                         min_node_x=min_node_x*k + k_shift_x
                         max_node_x=max_node_x*k + k_shift_x
                         min_node_y=min_node_y * k + k_shift_y
                         max_node_y=max_node_y * k + k_shift_y
                         cv2.line(img, (int(min_node_x), int(min_node_y)), (int(min_node_x), int(max_node_y)), lineclour, 1)
                    break
        count = 0
        for i_row in range(1, node_number_row_map + 1):
            count = count + 1
            if (count%2) == 0:
                lineclour = colourMap["black"]
            else:
                lineclour = colourMap["pink"]
            for i_col in range(1, node_number_col_map + 1):
                current_node = i_col + node_number_col_map * (i_row - 1)
                if current_node in boundary_nodes_y:
                    Node_array=boundary_nodes_y[current_node]
                    for i_node in range(1,len(Node_array),2):
                        min_node_x,min_node_y=AuxiliaryModule.convert_vertex_to_coordinate(node_number_col_map,Node_array[i_node-1])
                        max_node_x,max_node_y=AuxiliaryModule.convert_vertex_to_coordinate(node_number_col_map,Node_array[i_node])
                        min_node_x=min_node_x*k + k_shift_x
                        max_node_x=max_node_x*k + k_shift_x
                        min_node_y=min_node_y * k + k_shift_y
                        max_node_y=max_node_y * k + k_shift_y
                        cv2.line(img, (int(min_node_x), int(min_node_y)), (int(max_node_x), int(min_node_y)), lineclour, 1)
                    break

        for index in range(1,len(list)):
            if  list[index]["type"] == "Rectangl" :
                RectanglPoint = list[index]["point"]
                cv2.rectangle(img,
                             (int(RectanglPoint.p1.x)+2, int(RectanglPoint.p1.y)+2),
                               (int(RectanglPoint.p2.x)-2, int(RectanglPoint.p2.y)-2),
                               colourMap[list[index]["colour"]],
                                -1)
                #cv2.circle(img, (447, 63), 63, (0, 0, 255), -1)
            elif list[index]["type"] == "Circle":
                #cv2.rectangle(img, (384, 0), (510, 128), (0, 255, 0), 3)
                RectanglPoint = list[index]["point"]
                #print(RectanglPoint)
                cv2.circle(img, (int(RectanglPoint.p1.x), int(RectanglPoint.p1.y)), 0.1, colourMap[list[index]["colour"]], -1)
            else:
                print("负数")
        global backgroundimg
        backgroundimg = img


#        cv2.imshow('MAP', img)

        #cv2.destroyAllWindows()
    except Exception as e:
        #print(e)
        sys.exit(1)  # fatal error, need exit the program

def agvshelf(curfile):
    try:
        current_path = os.getcwd()
        file_path = current_path + "/SnapShots/2018-4-10_14-49-20_673.txt"
        config_reader = configparser.ConfigParser()
        config_reader.read(file_path)

        list, stime,scount = AuxiliaryModule.getAgvShelfInfoFromFile(curfile)
        for index in range(len(list)):
            list[index]["point"].p1.x = list[index]["point"].p1.x * k + k_shift_x
            list[index]["point"].p1.y = list[index]["point"].p1.y * k + k_shift_y
            list[index]["point"].p2.x = list[index]["point"].p2.x * k + k_shift_x
            list[index]["point"].p2.y = list[index]["point"].p2.y * k + k_shift_y

        global backgroundimg
        img = backgroundimg.copy()

        for index in range(len(list)):
            if list[index]["type"] == "Rectangl_agv":
                RectanglPoint = list[index]["point"]
                #print(RectanglPoint, colourMap[list[index]["colour"]])
                cv2.rectangle(img, (int(RectanglPoint.p1.x)+2, int(RectanglPoint.p1.y)+2),
                              (int(RectanglPoint.p2.x)-2, int(RectanglPoint.p2.y)-2),
                              colourMap[list[index]["colour"]], -2)
                # cv2.circle(img, (447, 63), 63, (0, 0, 255), -1)
                cv2.putText(img, str(list[index]["no"]), (int(RectanglPoint.p1.x), int(RectanglPoint.p1.y)),
                            chosen_font, k_text, (0, 0, 0), 1,cv2.FILLED)
            elif  list[index]["type"] == "Rectangl_shelf":
                RectanglPoint = list[index]["point"]
                cv2.rectangle(img, (int(RectanglPoint.p1.x)+2, int(RectanglPoint.p1.y)+2),
                              (int(RectanglPoint.p2.x)-2, int(RectanglPoint.p2.y)-2),
                              colourMap[list[index]["colour"]], -2)
            elif list[index]["type"] == "Circle":
                # cv2.rectangle(img, (384, 0), (510, 128), (0, 255, 0), 3)
                RectanglPoint = list[index]["point"]
                #print(RectanglPoint,int(RectanglPoint.p1.y))
                cv2.circle(img, (int(RectanglPoint.p1.x), int(RectanglPoint.p1.y)), 5,
                           colourMap[list[index]["colour"]], -1)
                cv2.putText(img, list[index]["no"], (int(RectanglPoint.p1.x), int(RectanglPoint.p1.y)),
                        chosen_font, k_text, (0, 0, 0), 1,cv2.FILLED)

            else:
                print("负数")
        size = img.shape
        aa = size[1]
        cv2.putText(img, "time:"+ stime, (30,size[0]-40 ), chosen_font, k_text, colourMap["pink"], 1,cv2.FILLED)
        cv2.putText(img, "file:" + curfile, (30, size[0] - 20), chosen_font, k_text, colourMap["pink"], 1, cv2.FILLED)
        cv2.putText(img, "Station_Visit_Count_Per_Second:" + scount, (500, size[0] - 20), chosen_font, k_text, colourMap["pink"], 1, cv2.FILLED)

        cv2.imshow('MAP', img)

        if cv2.waitKey(300) == 27:
            print("exit")
            raise Exception()
        # cv2.destroyAllWindows()
    except Exception as e:
        #print(e)
        sys.exit(1)  # fatal error, need exit the program



def drawmap_main(boundary_nodes_x,boundary_nodes_y):
    sleep_time = 0.2
    background(boundary_nodes_x, boundary_nodes_y)
    filelist = AuxiliaryModule.getAllFileName("./SnapShots/")
    for name in filelist:
        curfile = "./SnapShots/"+name
        agvshelf(curfile)
        time.sleep(sleep_time)



def drawmap_for_path_search(current_map,current_vertex, target_vertex):
    global vertex_layer_shift
    if vertex_layer_shift is None:
        vertex_layer_shift = ConfigManager.get_vertex_layer_shift()
    current_path = os.getcwd()
    file_path = current_path + "/config.ini"
    config_reader = configparser.ConfigParser()
    config_reader.read(file_path)
#    print('read configuration file: ' + file_path)

    map_area = AuxiliaryModule.convert_area_coordinates(config_reader.get('map', 'initial_area'))

    list = {}
    map_area.setFill("white")
    listindex = 0
    list[listindex] = {"point": map_area, "type": "Rectangl", "colour": "white", "no": 0}

    index=0
    list[index]["point"].p1.x = list[index]["point"].p1.x * k + k_shift_x
    list[index]["point"].p1.y = list[index]["point"].p1.y * k + k_shift_y
    list[index]["point"].p2.x = list[index]["point"].p2.x * k + k_shift_x
    list[index]["point"].p2.y = list[index]["point"].p2.y * k + k_shift_y

    griddingPoint = list[0]["point"]
    img = np.zeros((int(griddingPoint.p2.y) + map_padding_y, int(griddingPoint.p2.x) + map_padding_x, 3), np.uint8)
    # fill the image with white
    img.fill(255)
    node_number_col_map = int(config_reader.get('map', 'column_number'))
    for i_edge in [one for one in current_map.edges() if one[0] < vertex_layer_shift and one[1]<vertex_layer_shift]:
         lineclour = colourMap["black"]
         min_node_x, min_node_y = AuxiliaryModule.convert_vertex_to_coordinate(node_number_col_map,i_edge[0])
         max_node_x, max_node_y = AuxiliaryModule.convert_vertex_to_coordinate(node_number_col_map,i_edge[1])
         min_node_x = min_node_x * k + k_shift_x
         max_node_x = max_node_x * k + k_shift_x
         min_node_y = min_node_y * k + k_shift_y
         max_node_y = max_node_y * k + k_shift_y
         cv2.arrowedLine(img, (int(min_node_x), int(min_node_y)), (int(max_node_x), int(max_node_y)), lineclour, 1)

    for i_edge in [one for one in current_map.edges() if one[0] > vertex_layer_shift and one[1] > vertex_layer_shift]:
         lineclour = colourMap["black"]
         min_node_x, min_node_y = AuxiliaryModule.convert_vertex_to_coordinate(node_number_col_map,i_edge[0])
         max_node_x, max_node_y = AuxiliaryModule.convert_vertex_to_coordinate(node_number_col_map,i_edge[1])
         min_node_x = min_node_x * k + k_shift_x
         max_node_x = max_node_x * k + k_shift_x
         min_node_y = min_node_y * k + k_shift_y
         max_node_y = max_node_y * k + k_shift_y
         cv2.arrowedLine(img, (int(min_node_x), int(min_node_y)), (int(max_node_x), int(max_node_y)), lineclour, 1)

         node_x, node_y = AuxiliaryModule.convert_vertex_to_coordinate(node_number_col_map,current_vertex)
         node_x = node_x * k + k_shift_x
         node_y = node_y * k + k_shift_y
         cv2.line(img, (int(min_node_x), int(min_node_y)), (int(max_node_x), int(max_node_y)), lineclour, 1)
         cv2.rectangle(img, (int(node_x) + 2, int(node_y) + 2),
                  (int(node_x) - 2, int(node_y) - 2),
                  colourMap["red"], -2)

         node_x, node_y = AuxiliaryModule.convert_vertex_to_coordinate(node_number_col_map, target_vertex)
         node_x = node_x * k + k_shift_x
         node_y = node_y * k + k_shift_y
         cv2.line(img, (int(min_node_x), int(min_node_y)), (int(max_node_x), int(max_node_y)), lineclour, 1)
         cv2.rectangle(img, (int(node_x) + 2, int(node_y) + 2),
                      (int(node_x) - 2, int(node_y) - 2),
                      colourMap["green"], -2)
    cv2.imshow('MAP', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    pass


##################################################write results to files##################################################################
def write_positions_to_file(column_number, agv_info,static_shelves, other_information, time_run):
    try:
        array_shelves_index=list(static_shelves.keys())
        other_information_index=list(other_information.keys())
        current_path = os.getcwd()
        ms=int(time.time()*1000%1000)
        file_name=str(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))+'_'+str(ms).zfill(3)+".txt"
        file_path = current_path + "/SnapShots/"+file_name
        #file_path = current_path +"/agv_position.txt"
        file = configparser.ConfigParser()

        file.add_section('simulation')
        file.set('simulation','time',str(time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime(time_run))))

        file.add_section('agv information')
        for i_agv in range(1,len(agv_info)+1):
            file.set('agv information','agv_'+str(i_agv), str(agv_info[i_agv-1]))

        file.add_section('static shelves information')
        for i_shelf in range(1, len(array_shelves_index) + 1):
            file.set('static shelves information', 'static_shelves_' + str(array_shelves_index[i_shelf-1]), str(static_shelves[array_shelves_index[i_shelf-1]]))

        file.add_section('other information')
        for i_other in range(1,len(other_information_index)+1):
            file.set('other information',str(other_information_index[i_other-1]),other_information[other_information_index[i_other-1]])

#        static_shelves

        with open(file_path,'w') as fw:
            file.write(fw)

        return file_name

    except Exception as e:
        print(e)



def write_simulation_results_to_file(simulation_total_time,grid_length,agv_number,
                                     finished_package_count,waiting_count,agv_move_step_count,conf,
                                     simulation_start_time,efficient_info,agv_finished_package_count,agv_wait_times):
    simulation_end_time = time.time()
    current_path = os.getcwd()
    file_path = current_path + "\\" + "result information for analysis.txt"
    #
    with open(file_path,'w') as f:
        f.write('simulation_time = ' + str(simulation_total_time) + ' seconds\n')
        f.write('map grid_length = ' + str(grid_length) + '\n')
        f.write('in station bufffer len = ' + str(conf.max_buffer_len_per_in_station) + '\n')
        f.write('agv number = ' + str(agv_number)+'\n')
 #       f.write('agv speed = ' + str(agv_speed) + '\n')
        f.write('agv charge efficient = ' + str(conf.charge_efficient) + '\n')
        f.write('finished_package_count = ' + str(finished_package_count) + '\n')
        f.write('waiting_count = ' + str(waiting_count) + '\n')
        f.write('agv move step count = ' + str(agv_move_step_count) + '\n')
        simulation_efficiency_per_hour = round(finished_package_count * 3600 / (simulation_total_time +
            finished_package_count * (conf.cost_of_drop_package + conf.cost_of_put_package) / agv_number),1)
        simulation_efficiency_per_hour = round(simulation_efficiency_per_hour * conf.charge_efficient,1)
        f.write('simulation_efficiency_per_hour = ' + str(simulation_efficiency_per_hour) + '\n')
        if agv_number > 0:
            simulation_efficiency_per_agv_per_hour = round(simulation_efficiency_per_hour / agv_number, 1)
            f.write('simulation_efficiency_per_agv_per_hour = ' + str(simulation_efficiency_per_agv_per_hour) + '\n')

        if finished_package_count > 0:
            average_agv_travel_distance_per_package = round(agv_move_step_count * grid_length / finished_package_count, 1)
            f.write('average_agv_travel_distance_per_package = ' + str(average_agv_travel_distance_per_package) + ' m' + '\n')
            f.write( 'average_agv_wait_times_per_package = ' + str(round(waiting_count / finished_package_count, 1)) + '\n')
        program_running_time = round(simulation_end_time - simulation_start_time, 1)
        f.write('program_running_time = ' + str(program_running_time) + ' seconds' + '\n')

        f.write(efficient_info)

        f.write('******************************************************' + '\n')
        config_info = ConfigManager.read_config_info()
        f.write(config_info)

        f.write('******************************************************' + '\n')
        for agv_seq_no in range(1, agv_number + 1):
            f.write('agv ' + str(agv_seq_no) + ' finished ' + str(
                agv_finished_package_count[agv_seq_no - 1]) + ' packages  ' + 'wait times ' + str(
                agv_wait_times[agv_seq_no - 1]) + '\n')
##################################################results efficient information##################################################################
def efficient_information(simulation_steps,simulation_progress,simulation_progress_time,
                          simulation_start_time,step,grid_step_time,waiting_count,agv_number,
                          finished_package_count,conf,shelves_package_count,out_station_package_count,efficient_info):
    simulation_current_progress = step / simulation_steps
    simulation_current_time = time.time()
    if (simulation_current_progress - simulation_progress) >= 0.005 and (
            simulation_current_time - simulation_progress_time) >= 5:
        simulation_progress = simulation_current_progress
        simulation_progress_time = simulation_current_time

        step_efficient_info = '*****************************************\r\n'

        program_running_time = round(simulation_progress_time - simulation_start_time, 1)
        # print('program_running_time = ', program_running_time)

        step_efficient_info += 'simulation_progress: ' + str(round(simulation_progress * 100, 2)) + '%\r\n'

        simulation_real_time = step * grid_step_time
        step_efficient_info += 'simulation_real_time = ' + str(round(simulation_real_time, 1)) + '\r\n'

        waiting_percentage = waiting_count / step / agv_number
        step_efficient_info += 'waiting_percentage = ' + str(round(waiting_percentage, 2)) + '\r\n'

        simulation_efficiency_per_hour = round(finished_package_count * 3600 /
                                               (simulation_real_time + finished_package_count * (
                                                           conf.cost_of_drop_package + conf.cost_of_put_package) / agv_number)
                                               , 1)
        simulation_efficiency_per_hour = round(simulation_efficiency_per_hour * conf.charge_efficient, 1)
        # print('simulation_efficiency_per_hour = ', simulation_efficiency_per_hour)
        simulation_efficiency_per_agv_per_hour = round(simulation_efficiency_per_hour / agv_number, 1)
        step_efficient_info += 'simulation_efficiency_per_agv_per_hour = ' + str(
            simulation_efficiency_per_agv_per_hour) + '\r\n'

        step_efficient_info += 'in_station_package_count: ' + str(shelves_package_count) + '\r\n'
        step_efficient_info += 'out_station_package_count: ' + str(out_station_package_count) + '\r\n'

#        print(step_efficient_info)
        efficient_info += step_efficient_info

