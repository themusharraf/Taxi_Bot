from json import load

region_list = []

with open(r'C:\Py\taksi_bot\reg_dis.json') as f:
    d: dict = load(f)
    for region in d.keys():
        region_list += [region]


def get_districts_by_region(region_name):
    with open(r'C:\Py\taksi_bot\reg_dis.json') as f:
        data: dict = load(f)
        districts = data.get(region_name)
        return districts


car_names = ['Captiva', 'Gentra', 'Cobalt', 'Nexia (Ravon)', 'Nexia (2)', 'Nexia', 'Spark', 'Matiz', 'Lada Largus', 'Inomarka'] # noqa