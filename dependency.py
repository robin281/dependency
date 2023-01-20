from parent_child import Parent_child_parser as p

import ruamel.yaml
from yaml_util import Yaml_util as y
import copy
import logger
from output import Output as o
import device

tables = {}
pc = p("parent_child.txt")
print(pc.get_parent_modes("aaa-user"))
print(pc.get_parent_modes("main-cpu"))
submode_list = pc.get_submode_list()
print(pc.get_mode_entering_cli("main-cpu"))
output_yaml = {}
history = {}
yaml = ruamel.yaml.YAML()

out = o()
out.clean_dir("output")
out.create_dir("output")

def is_duplicate_entry(mode, cli_list):
    try:
        list_of_clis = history[mode]
        print(list_of_clis)
        print(cli_list)
        for cli in list_of_clis:
            if cli_list == cli:
                logger.logging.info("List of CLI's are already present in mode level  dependency file - Ignoring")
                return True
        return False

    except KeyError:
        return False
    

for modes in submode_list:
    dep_file = "dependent-"+modes.strip().replace("-", "_") + "-platform.yaml"
    output_list = []
    try:
        with open("dep/"+dep_file) as f:
            logger.logging.info("Processing dependent file - " + dep_file)
            logger.logging.info("==========================================")
            yaml.preserve_quotes = True
            data = yaml.load(f)
            temp_data = copy.deepcopy(data)

            y_util = y()
            for x,z in data.items():
                flag_dict = {}
                flag = y_util.get_action_type(z)
                flag_dict['flags'] = flag
                tables[x] = flag_dict
                if y_util.is_global_mode(flag):
                    logger.logging.info("GLOBAL_MODE dependency found for table " + x)
                    f = 'FUZZER_GLOBAL_MODE'
                    cli_list = y_util.get_cli_list(z, f)
                    logger.logging.info("CLI list to be added")
                    logger.logging.info(cli_list)
                    if not is_duplicate_entry(modes, cli_list):
                        for cli in cli_list:
                            output_list.append('\"' + cli + '\"')
                        try:
                            history[modes].append(cli_list)
                        except KeyError:
                            history[modes] = []
                            history[modes].append(cli_list)
                        # copy data to output
                    print(history)
                    temp_data = y_util.cleanup_yaml_dict(temp_data, x, f)
                    temp_data = y_util.delete_table_entry(temp_data,x)

            temp_yaml_dict = {}
            for x, z in data.items():
                flag = tables[x]['flags']
                if y_util.is_replace_all(flag):
                    logger.logging.info("REPLACE ALL dependency found for table " + x)
                    global_list = []
                    same_mode_list = []
                    
                    ra = 'FUZZER_REPLACE_ALL'
                    cli_list_rep_all = y_util.get_cli_list(z, ra)
                    #print(cli_list_rep_all)
                    dick = device.configure_cli_list(cli_list_rep_all)
                    if dick is None:
                        logger.logging.error("FAILED")
                        continue 
                    try:
                        if dick[cli_list_rep_all[-1]][0] != modes:
                            logger.logging.error("DEP file for table "+ x+ " is incorrect")
                            continue
                    except KeyError:
                        logger.logging.error("last CLI is not configurable")
                        continue

                    temp_list = []
                    new_cli_list = []
                    index = -1
                    i = 0
                    for clis in cli_list_rep_all:
                        if dick[clis][0] == 'configure' and dick[clis][1] == 'configure':
                            global_list.append(clis)
                        else :
                            new_cli_list.append(clis)
                    
                    first_list = []
                    second_list = []
                    last_configure_index = -1
                    for i, item in enumerate(new_cli_list):
                        if dick[item][0] == 'configure':
                            last_configure_index = i

                    if last_configure_index == -1:
                        second_list = new_cli_list
                    else:
                        for i, item in enumerate(new_cli_list):
                            if i <= last_configure_index:
                                first_list.append(item)
                            else:
                                second_list.append(item)

                    if len(first_list) != 0:
                        global_list.extend(first_list)

                    temp_list = []
                    mode_cli_found = False
                    for item in second_list:
                        if mode_cli_found is True:
                            same_mode_list.append(item)
                        else:
                            temp_list.append(item)           
                        if dick[item][0] == modes:
                            mode_cli_found = True

                    parent_child_cli_list = []
                    parent_child_h = []
                    parent_child_h = pc.get_parent_modes(modes)
                    
                    
                    parent_child_cli_list = pc.get_cli_list(parent_child_h)
                    parent_child_cli_list.append(pc.get_mode_entering_cli(modes))
                    print("parent_child_h is " + str(parent_child_h))

                    temp_data = y_util.cleanup_yaml_dict(temp_data, x, 'FUZZER_REPLACE_ALL')
                    temp_data = y_util.delete_table_entry(temp_data,x)

                    not_matched = False
                    if temp_list != parent_child_cli_list:
                        if temp_list[:-1] == parent_child_cli_list[:-1]:
                            new_dep = y_util.add_yaml_dict(temp_list[len(temp_list)-1], 'FUZZER_REPLACE_PARENT')
                            print("robin: am i here" + str(new_dep))
                        else:
                            new_dep = y_util.add_yaml_dict(temp_list, 'FUZZER_REPLACE_ALL')
                            print("robin: am i here 2" + str(new_dep)) 
                        try :
                            temp_data[x].append(new_dep)
                            print("robin: am i here 3" + str(new_dep))
                        except KeyError:
                            temp_data[x] = []
                            temp_data[x].append(new_dep)
                            print(temp_data[x])
                            print("robin: am i here 4" + str(new_dep)) 
                        not_matched = True

                    
                    if len(same_mode_list) is not 0:
                        if not_matched is False:
                            global_list.extend(parent_child_cli_list)
                            global_list.extend(same_mode_list)
                        else :
                            global_list.extend(temp_list)
                            global_list.extend(same_mode_list)
                    
                    if not is_duplicate_entry(modes, global_list):
                        for cli in global_list:
                            output_list.append('\"' + cli + '\"')
                        try:
                            history[modes].append(global_list)
                        except KeyError:
                            history[modes] = []
                            history[modes].append(global_list)                    
                        




                    
                    print("LISTS: for table" + x)
                    print(global_list)
                    print(temp_list)
                    print(parent_child_cli_list)

            
            for x, z in data.items():
                flag = tables[x]['flags']
                if y_util.is_same_mode(flag) and y_util.is_replace_parent(flag):
                    logger.logging.info("SAME MODE and REPLACE PARENT dependency found for table "+ x)
                    heirarchy = []
                    p_modes = []
                    p_modes = pc.get_parent_modes(modes)

                    heirarchy = pc.get_cli_list(p_modes)
                    
                    heirarchy.append(pc.get_mode_entering_cli(modes))

                    rp = 'FUZZER_REPLACE_PARENT'
                    cli_list_rep_par = y_util.get_cli_list(z, rp)
                    for c_list in cli_list_rep_par:
                        heirarchy.append(c_list)

                    s = 'FUZZER_SAME_MODE'
                    cli_list_same_mode = y_util.get_cli_list(z, s)
                    for c_list in cli_list_same_mode:
                        heirarchy.append(c_list)
                    
                    for x in range(1 , len(p_modes)):
                        heirarchy.append("exit")
                    
                    logger.logging.info("CLI list to be added")
                    logger.logging.info(heirarchy)

                    if not is_duplicate_entry(modes, heirarchy):
                        for cli in heirarchy:
                            output_list.append('\"' + cli + '\"')
                        try:
                            history[modes].append(heirarchy)
                        except KeyError:
                            history[modes] = heirarchy
                        print(history)
                    
                    temp_data = y_util.cleanup_yaml_dict(temp_data, x, 'FUZZER_SAME_MODE')
                    temp_data = y_util.delete_table_entry(temp_data,x)
                
                elif y_util.is_same_mode(flag):
                    logger.logging.info("ONLY SAME MODE  dependency found for table "+ x)
                    heirarchy = []
                    p_modes = []
                    p_modes = pc.get_parent_modes(modes)
                    heirarchy = pc.get_cli_list(p_modes)

                    heirarchy.append(pc.get_mode_entering_cli(modes))

                    s = 'FUZZER_SAME_MODE'
                    cli_list_same_mode = y_util.get_cli_list(z, s)
                    for c_list in cli_list_same_mode:
                        heirarchy.append(c_list)
                    
                    for val in range(0 , len(p_modes)):
                        heirarchy.append("exit")
                    logger.logging.info("CLI list to be added")
                    logger.logging.info(heirarchy)

                    if not is_duplicate_entry(modes, heirarchy):
                        for cli in heirarchy:
                            output_list.append('\"' + cli + '\"')
                        try:
                            history[modes].append(heirarchy)
                        except KeyError:
                            history[modes] = heirarchy
                    
                    
                    temp_data = y_util.cleanup_yaml_dict(temp_data, x, 'FUZZER_SAME_MODE')
                    temp_data = y_util.delete_table_entry(temp_data,x)
                     

                    


            if len(output_list) != 0: 
                output_yaml[modes] = output_list
            #print(output_yaml)
            #print(temp_data)
            
            if len(temp_data) != 0:
                out.dump_dependent_file(dep_file, temp_data)
            logger.logging.info("==========================================")


    except FileNotFoundError:
        logger.logging.debug("Dependency file for" + modes + " Not present")
        m = 0
    
print(output_yaml)
out.dump_global_dependent_yaml(output_yaml)


