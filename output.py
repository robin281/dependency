import os
import errno
import logger
import ruamel.yaml
import shutil


class Output:
    def __init__(self):
        output = {}
    
    def create_dir(self, path):
        try:
            os.mkdir(path)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                logger.logging.error("directory creation failed" + str(exc.errno))
            logger.logging.error("directory already present "+ path)
    
    def clean_dir(self, path):
        try:
            shutil.rmtree(path)
            logger.logging.info("Directory '% s' has been removed successfully" % path)
        except OSError as error:
            if error == FileNotFoundError:
                logger.logging.debug("Nothing to clean")
            else:
                logger.logging.error("Directory '% s' can not be removed" % path)
                logger.logging.error(str(error))


    def dump_global_dependent_yaml(self, data):
        #data_t = yaml.safe_load(data)
        yaml = ruamel.yaml.YAML()
        yaml.indent(sequence=4, offset=2)
        yaml.preserve_quotes = True
        with open('output/temp.yaml', 'w') as yaml_file:
            yaml.dump(data, yaml_file)
        with open('output/temp.yaml', 'r') as infile, \
            open(r'output/mode-dep-cmd-platform.yaml', 'w') as outfile:
            data = infile.read()
            data = data.replace("'", "")
            outfile.write(data)
        os.remove('output/temp.yaml')

    def dump_dependent_file(self, file, data):
        yaml = ruamel.yaml.YAML()
        yaml.indent(sequence=4, offset=2)
        yaml.preserve_quotes = True
        
        with open('output/temp.yaml', 'w') as yaml_file:
            yaml.dump(data, yaml_file)
        with open('output/temp.yaml', 'r') as infile, \
            open(r'output/'+file, 'w') as outfile:
            data = infile.read()
            data = data.replace("'", "")
            outfile.write(data)
        os.remove('output/temp.yaml')
        


        