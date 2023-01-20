

from pyats.topology import loader
import re
import logger

def configure_cli_list(cli_list):
    tb_file = "testbed.yaml"
    tb = loader.load(tb_file)
    dev = tb.devices['uut1']
    dev.connect()
    dev.execute("clear logging")
    print(cli_list)
    try :
        dev.configure('\n'.join(cli_list))
    except:
        logger.logging.debug("some subcommand failed")

    output = dev.execute("show logging")
    log_parts = output.split("Log Buffer")
    output = log_parts[1]
    lines = output.split('\n')

    dict = {}
    for line in lines:
        if "robising" in line:
            t = {}
            temp = re.findall(r'\[(.*?)\]', line)
            print(temp[1])
            temp[1] = re.sub(' +', ' ', temp[1])
            dict[temp[1].strip()] = []
            temp[3] = re.sub(' +', ' ', temp[3])
            dict[temp[1].strip()].append(temp[3].strip())
    #print(dict)

    dict[cli_list[0]].append('configure')
    print(dict)
    print(cli_list)
    try :
        for i in range(1, len(cli_list)):
            dict[cli_list[i]].append(dict[cli_list[i-1]][0])
    except KeyError:
        logger.logging.error("dependency written for this table is wrong, try to configure manually")
        dev.disconnect()
        return None

    print(dict)


    #dict[cli_list[0]] 
    #for clis in cli_list:

    dev.disconnect()
    return dict
    
#print(dict) 


#print(output)

#dev.disconnect()

#print(output)
