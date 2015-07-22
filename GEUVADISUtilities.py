__author__ = 'heroico'


class GEUVADISFilteredFilesBuilder(object):
    def __init__(self, input_path, output_path, all_people, selected_people_by_id, snps_dict):
        self.input = input_path
        self.output = output_path
        self.all_people = all_people
        self.selected_people_by_id = selected_people_by_id
        self.snps_dict = snps_dict

    def run(self):
        pass