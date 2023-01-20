import logger
import re

class Yaml_util:
    def get_action_type(self, data):
        flag = 0
        
        for z in data:
            if z['Action'] == 'FUZZER_ALL_INPUT':
                flag = flag | 1
            if z['Action'] == 'FUZZER_REPLACE_ALL':
                flag = flag | (1<<1)
            if z['Action'] == 'FUZZER_SAME_MODE':
                flag = flag | (1<<2)  
            if z['Action'] == 'FUZZER_REPLACE_PARENT':
                flag = flag | (1<<3)
            if z['Action'] == 'FUZZER_GLOBAL_MODE':
                flag = flag | (1<<4)
        return flag

    def is_all_input(self, flag):
        if flag & 1 != 0:
            return True
        return False
    
    def is_same_mode(self, flag):
        if flag & (1<<2) != 0:
            return True
        return False
    
    def is_replace_parent(self, flag):
        if flag & (1<<3) != 0:
            return True
        return False

    def is_global_mode(self, flag):
        if flag & (1<<4) != 0:
            return True
        return False
    
    def is_replace_all(self, flag):
        if flag & (1<<1) != 0:
            return True
        return False

            

    def cleanup_yaml_dict(self, data, table, flag):
        cli_dict = data[table]
        for z in cli_dict:
            if z['Action'] == flag:
                cli_dict.remove(z)
        logger.logging.info("cleaning up " + str(z) +" from dependent file for table " + table)
        return data

    def delete_table_entry(self, data, table):
        if data[table] == []:
            try:
                logger.logging.info("table "+ table +" is empty after cleanup")
                logger.logging.info("deleting entry for table " + table)
                del data[table]
            except:
                logger.logging.error("No valid table to delete "+ table)
        return data

    def get_cli_list(self, table_data, flag):
        cli_list = []
        for z in table_data:
            if z['Action'] == flag:
                for cli in z['Commands']:
                    cli = re.sub(' +', ' ', cli)
                    cli_list.append(cli)
                return cli_list
        return None

    def add_yaml_dict(self, cli_list, flag):
        output = {}
        output['Action'] = flag 
        if isinstance(cli_list, str):
            cli_list = [cli_list]
        for index in range(0,len(cli_list)):
            cli_list[index] = '\"' + cli_list[index] + '\"'

        output['Commands'] = cli_list
        return output

        




