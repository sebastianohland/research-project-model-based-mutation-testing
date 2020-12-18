import json
import copy
import os
from classes.Model import Model


def import_data(file_path):
    """Imports JSON data with file path and returns dictionary of data."""
    with open(file_path) as infile:
        data = json.load(infile)
    return data


def export_json(filename, data):
    """Exports dictionary as json file."""
    with open(filename + ".json", "w") as f:
        json.dump(data, f, indent=4)


def export_models(model_list, folder_name):
    """Exports all mutations in model_list as separate json files to folder named folder_name"""
    model_names = ""
    # Creates folder if not exists
    os.makedirs(os.path.dirname(folder_name + "/"), exist_ok=True)
    for i in model_list:
        filename = folder_name + "/" + i.model['models'][0]['description']
        export_json(filename, i.model)
        model_names += i.model['models'][0]['description'] + "\n"
    # Outputs csv file of model names
    with open(folder_name + "/" + "namelist.csv", "w") as f:
        f.write(model_names)


def create_re_mutations(model, n_edges):
    """Input: Single model as a dict, number of edges in model.
    Returns: List off all possible mutations with one edge removed"""
    re_mutations = []
    print("Creating RE mutations...")
    for i in range(n_edges):
        # Creates a new model. Need to use deepcopy when copying a dictionary
        mutation = Model(copy.deepcopy(model))
        # Creates a name for model and saves it in 'description', will be used when creating namelist of models
        mutation.model['models'][0]['description'] = mutation.name + "_RE_{}_{}".format(mutation.edges[i]['id'],
                                                                                        mutation.edges[i]['name'])
        # The mutation is happening here
        mutation.remove_edge(i)
        # Appends mutation to mutation list
        re_mutations.append(mutation)
    print("RE mutations finished!")
    return re_mutations


def create_rv_mutations(model, n_vertices):
    """Input: Single model as a dict, number of vertices in model.
    Returns: List off all possible mutations with one vertex removed"""
    rv_mutations = []
    print("Creating RV mutations...")
    for i in range(n_vertices):
        mutation = Model(copy.deepcopy(model))
        mutation.model['models'][0]['description'] = mutation.name + "_RV_{}_{}".format(mutation.vertices[i]['id'],
                                                                                        mutation.vertices[i]['name'])
        mutation.remove_vertex(i)
        rv_mutations.append(mutation)
    print("RV mutations finished!")
    return rv_mutations


def create_red_mutations(model, n_edges):
    """Input: Single model as a dict, number of edges in model.
    Returns: List off all possible mutations with one edge reversed (sourceVertexId = targetVertexId and vice versa)"""
    red_mutations = []
    print("Creating RED mutations...")
    for i in range(n_edges):
        mutation = Model(copy.deepcopy(model))
        mutation.model['models'][0]['description'] = mutation.name + "_RED_{}_{}".format(mutation.edges[i]['id'],
                                                                                         mutation.edges[i]['name'])
        mutation.reverse_edge(i)
        red_mutations.append(mutation)
    print("RED mutations finished!")
    return red_mutations


def create_ceso_mutations(model, n_edges):
    """Input: Single model as a dict, number of edges in model.
    Returns: List off all possible mutations with one edge source changed to another random vertex."""
    ceso_mutations = []
    print("Creating CESR mutations...")
    for i in range(n_edges):
        mutation = Model(copy.deepcopy(model))
        mutation.model['models'][0]['description'] = mutation.name + "_CESO_{}_{}".format(mutation.edges[i]['id'],
                                                                                          mutation.edges[i]['name'])
        mutation.change_source(i)
        ceso_mutations.append(mutation)
    print("CESR mutations finished!")
    return ceso_mutations


def create_cesi_mutations(model, n_edges):
    """Input: Single model as a dict, number of edges in model.
    Returns: List off all possible mutations with one edge sink changed to another random vertex."""
    cesi_mutations = []
    print("Creating CESI mutations...")
    for i in range(n_edges):
        mutation = Model(copy.deepcopy(model))
        mutation.model['models'][0]['description'] = mutation.name + "_CESI_{}_{}".format(mutation.edges[i]['id'],
                                                                                          mutation.edges[i]['name'])
        mutation.change_sink(i)
        cesi_mutations.append(mutation)
    print("CESI mutations finished!")
    return cesi_mutations


def create_rafe_mutations(model, n_edges):
    """Input: Single model as a dict, number of edges in model.
    Returns: List off all possible mutations with one edge action removed."""
    rafe_mutations = []
    print("Creating RAFE mutations...")
    for i in range(n_edges):
        if "actions" in model['models'][0]['edges'][i]:     # Creates mutation only if edge contains action.
            mutation = Model(copy.deepcopy(model))
            mutation.model['models'][0]['description'] = mutation.name + "_RAFE_{}_{}".format(mutation.edges[i]['id'],
                                                                                              mutation.edges[i]['name'])
            mutation.remove_action(i)
            rafe_mutations.append(mutation)
    print("RAFE mutations finished!")
    return rafe_mutations


def create_raf_mutations(model, n_edges):
    """Input: Single model as a dict, number of edges in model.
    Returns: List off all possible mutations with one edge action replaced with another random edge action."""
    raf_mutations = []
    print("Creating RAF mutations...")
    for i in range(n_edges):
        if "actions" in model['models'][0]['edges'][i]:     # Creates mutation only if edge contains action.
            mutation = Model(copy.deepcopy(model))
            mutation.model['models'][0]['description'] = mutation.name + "_RAF_{}_{}".format(mutation.edges[i]['id'],
                                                                                             mutation.edges[i]['name'])
            mutation.replace_action(i)
            raf_mutations.append(mutation)
    print("RAF mutations finished!")
    return raf_mutations


def main():
    # Import model from JSON file and convert to dictionary
    print("Importing file...")
    original_model = import_data("../models/PetClinicFull.json")    # Put filepath to model here!!
    n_edges = len(original_model['models'][0]['edges'])
    n_vertices = len(original_model['models'][0]['vertices'])
    print("Number of edges: {}".format(n_edges))
    print("Number of vertices: {}".format(n_vertices))
    print("----------------------------------------------------------")

    # Lists of mutation methods:
    # RE = Remove edge
    # RV = Remove vertex
    # RED = Reverse edge direction
    # CESO = Change edge source to another random vertex
    # CESI = Change edge sink to another random vertex
    # RAFE = Remove action from edge
    # RAF = Replace action with another random action from the same FSM

    # Generating mutations
    re_mutations = create_re_mutations(original_model, n_edges)
    rv_mutations = create_rv_mutations(original_model, n_vertices)
    red_mutations = create_red_mutations(original_model, n_edges)
    ceso_mutations = create_ceso_mutations(original_model, n_edges)
    cesi_mutations = create_cesi_mutations(original_model, n_edges)
    rafe_mutations = create_rafe_mutations(original_model, n_edges)
    raf_mutations = create_raf_mutations(original_model, n_edges)

    # Exporting mutations to separate folders
    print("Exporting mutation models...")
    export_models(re_mutations, "RE_Mutations")
    export_models(rv_mutations, "RV_Mutations")
    export_models(red_mutations, "RED_Mutations")
    export_models(ceso_mutations, "CESO_Mutations")
    export_models(cesi_mutations, "CESI_Mutations")
    export_models(rafe_mutations, "RAFE_Mutations")
    export_models(raf_mutations, "RAF_Mutations")
    print("Exporting finished!")


if __name__ == "__main__":
    main()
