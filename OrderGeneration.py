import random
import bisect

def random_order_generation(item_line_possibility,Item_pod_Layer,num_lines):
    try:
        item_selected=[]
        for i_line in range(1, num_lines + 1):
            randomnum = random.random()
            if randomnum in item_line_possibility:
                item_selected.append([item_line_possibility.index(randomnum)+1])
            else:
                bisect.insort(item_line_possibility, randomnum)
                item_selected.append([item_line_possibility.index(randomnum)+1])
                item_line_possibility.remove(randomnum)
        for eachelement in item_selected:
           eachelement.append(Item_pod_Layer['item_' + str(eachelement[0])][0][2])
        return item_selected
    except Exception as e:
        print('random_order_generation: '+repr(e))
        return []

def random_replen_order_generation(pod_called_count_array,total_count, pod_called_count_for_replen,replenishing_task_info, replen_stations,i_station,replenishing_time):
    pod_count_possibility=[x[1] for x in pod_called_count_array]
    pod_count_possibility.sort()
    random_num=random.uniform(min(pod_count_possibility),max(pod_count_possibility))
    pod_called_count_array.sort(key=(lambda x: x[1]))
    if random_num in pod_count_possibility:
        index = pod_count_possibility.index(random_num)
        stationi_replenishing_info_temp = [x for x in replenishing_task_info if x[0] == [replen_stations[i_station - 1]]][0]
        replenishing_task_info.remove(stationi_replenishing_info_temp)
        replenishing_task_info.append([replen_stations[i_station - 1],replenishing_time, pod_called_count_array[index][0]])
        pod_called_count_for_replen[pod_called_count_array[index][0]]=0
    else:
        bisect.insort(pod_count_possibility, random_num)
        index=pod_count_possibility.index(random_num)
        stationi_replenishing_info_temp = [x for x in replenishing_task_info if x[0] == replen_stations[i_station - 1]][0]
        replenishing_task_info.remove(stationi_replenishing_info_temp)
        replenishing_task_info.append([replen_stations[i_station - 1],replenishing_time, pod_called_count_array[index][0]])
        pod_count_possibility.remove(random_num)
        pod_called_count_for_replen[pod_called_count_array[index][0]]=0
