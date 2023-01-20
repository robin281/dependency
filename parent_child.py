class Parent_child_parser:
    def __init__(self, file):
        self.file =  file
        self.parsed_parent_child_dict = {}
        self.mode_to_cli_dict = {}

    def get_parent_modes(self, mode):
        parent_list = []
        mode_input = mode
        if not self.parsed_parent_child_dict:
            lines = []
            with open(self.file) as stream:
                lines = stream.readlines()
                count = 0
                for line in lines:
                    count += 1
                    parent_line_list = line.split(',')
                    mode_name = ''
                    content_dict = {}
                    for p_line in parent_line_list:
                        if ':' in p_line:
                            line_content = p_line.split(':')
                            if 'Mode' in line_content[0]:
                                mode_name = line_content[1]
                            content_dict[line_content[0].strip()] = line_content[1].strip()
                    self.parsed_parent_child_dict[mode_name] = content_dict

        while (1):
            value = self.parsed_parent_child_dict[mode_input]
            parent_name = value['Parent_m']
            parent_list.append(parent_name)
            if (parent_name == 'configure'):
                break
            mode_input = parent_name
        return parent_list

    def get_submode_list(self):
        submode_list = []
        for x, y in self.parsed_parent_child_dict.items():
            submode_list.append(x)
        return submode_list
    
    def get_mode_entering_cli(self, mode):
        return self.parsed_parent_child_dict[mode]['Command']

    def get_cli_list(self, p_list):
        cli_list = []
        #p_list = p_list[::-1]
        for parent in p_list:
            if (parent != "configure"):
                cli_list.append(self.get_mode_entering_cli(parent))
        return cli_list

    