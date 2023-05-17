import pandas as pd
from parse import compile
from absl import flags
from absl import app
import copy
import math 
from IPython.display import display
pd.set_option('display.max_row', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define input arguments
FLAGS = flags.FLAGS
flags.DEFINE_string("vlg", "./synth_vlg/synth_full_adder.v", "target verilog filepath")
flags.DEFINE_string("clib", "./yosys_script/sfq_cells.v", "cell libaray used to synthesize the target verilog")
flags.DEFINE_string("loop", "False", "enable loop analysis or not")
flags.DEFINE_string("outdir", "./unit_csv", "output directory")
flags.DEFINE_string("un", None, "target_unit_name")


# Global variables
node_list = []
i_node_list = []    # input node list
o_node_list = []    # output node list

class Node:
    def __init__(self, node_type, node_name,\
                 name_A, name_B, name_Q):
        self.node_type = node_type
        self.node_name = node_name 
        self.name_A = name_A
        self.name_B = name_B
        self.name_Q = name_Q
        self.parent_A = None
        self.parent_B = None
        self.depth_A = 0
        self.depth_B = 0
        self.children = []
      
        self.visit_A = False
        self.visit_B = False
        self.visit = False

        self.num_split = 0
        self.depth_split = 0

    def print(self):
        print("node_type: ", self.node_type)
        print("node_name: ", self.node_name)
        print("name_A: ", self.name_A)
        print("name_B: ", self.name_B)
        print("name_Q: ", self.name_Q)
        print("depth_A: ", self.depth_A)
        print("depth_B: ", self.depth_B)
        if self.parent_A is not None:
            print("parent_A: ", self.parent_A.node_name)
        else:
            print("parent_A: None")
        if self.parent_B is not None:
            print("parent_B: ", self.parent_B.node_name)
        else:
            print("parent_B: None")
        print("children: ")
        for child in self.children:
            print(child.node_name)
        print("visit_A: ", self.visit_A)
        print("visit_B: ", self.visit_B)
        print("depth_split: ", self.depth_split)
        print("num_split: ", self.num_split)
        
        print()
        return

    
    def remove(self):
        if self.parent_A is not None:
            for it in self.parent_A.children:
                if it.node_name == self.node_name:
                    self.parent_A.children.remove(it)
        if self.parent_B is not None:
            for it in self.parent_B.children:
                if it.node_name == self.node_name:
                    self.parent_B.children.remove(it)

        for child in self.children:
            if child.parent_A and child.parent_A.node_name == self.node_name:
                child.parent_A = None
            if child.parent_B and child.parent_B.node_name == self.node_name:
                child.parent_B = None

        self.parent_A = None
        self.parent_B = None
        self.children = []

        return


def init_visit():
    global node_list

    for node in node_list:
        node.visit_A = False
        node.visit_B = False
        node.visit = False
    return


def gen_cell_list(clib_path):
    cell_name_list = []
    
    g_format = compile("module {}({});")
    clib = open(clib_path, "r")

    for line in clib:
        line = ' '.join(line.split())
        try:
            cell_name, _ = g_format.parse(line)
        except:
            continue
        cell_name_list.append(cell_name)

    return cell_name_list


def gen_node_list(vlg_path, clib_path):
    global node_list
    global cell_param_df

    i_format_s = compile("input {};")
    i_format_m = compile("input [{}:0] {};")
    o_format_s = compile("output {};")
    o_format_m = compile("output [{}:0] {};")
    g_format = compile(".{}({})")
    as_format = compile("assign {} = {};")

    cell_name_list = gen_cell_list(clib_path)

    vlg = open(vlg_path, "r")
    for line in vlg:
        line = ' '.join(line.split())
        if len(line.split()) == 0:
            continue
        if "*" in line:
            continue
        
        # Input node
        if "input" in line and not "module" in line and not "assign" in line:
            if len(line.split()) > 2:
                bit_width, name = i_format_m.parse(line)
                bit_width = int(bit_width) + 1
                #print(line, name, bit_width)
                for i in range(0, bit_width):
                    node = Node(node_type = 'input',
                                node_name = "{}[{}]".format(name, i),
                                name_A = None,
                                name_B = None, 
                                name_Q = "{}[{}]".format(name, i)
                                )
                    node_list.append(node)

            else:
                name, = i_format_s.parse(line)
                node = Node(node_type = 'input',
                            node_name = name,
                            name_A = None, 
                            name_B = None,
                            name_Q = name
                            )
                node_list.append(node)

        # Output node
        if "output" in line and not "module" in line and not "assign" in line:
            #print(line)
            if len(line.split()) > 2:
                bit_width, name = o_format_m.parse(line)
                bit_width = int(bit_width) + 1
                for i in range(0, bit_width):
                    node = Node(node_type = 'output', 
                                node_name = "{}[{}]".format(name, i),
                                name_A = "{}[{}]".format(name, i),
                                name_B = None,
                                name_Q = None
                                )
                    node_list.append(node)

            else:
                name, = o_format_s.parse(line)
                node = Node(node_type = 'output', 
                            node_name = name,
                            name_A = name,
                            name_B = None,
                            name_Q = None 
                            )
                node_list.append(node)
            
        # Gate node
        node_type = None
        name_A = None
        name_B = None
        name_Q = None

        for cell_name in cell_name_list:
            ls = line.split()
            if cell_name == ls[0]:
                node_name = ls[1]
                node_type = cell_name
                while(True):
                    line = ' '.join(vlg.readline().split())
                    line = line.replace(',', '')
                    if ';' in line:
                        break;
                    
                    net, name = g_format.parse(line)
                    if net == 'A':
                        name_A = name
                    if net == 'B':
                        name_B = name
                    if net == 'Q':
                        name_Q = name
                # IK: corner handling in revision 
                if node_type == 'BUFFT_RSFQ':
                    node_type = 'DFFT_RSFQ'
                # IK: end
                node = Node(node_type = node_type, 
                            node_name = node_name,
                            name_A = name_A, 
                            name_B = name_B, 
                            name_Q = name_Q
                            )
                node_list.append(node)

        
        # IK: Assign handling 
        if "assign" in line:
            dst, src = as_format.parse(line)
            #print("dst: {}, src: {}".format(dst, src))
            for node in node_list:
                if src == node.name_Q:
                    for node_it in node_list:
                        if dst == node_it.name_A or dst == node_it.name_B:
                            node.name_Q = dst
                        else:
                            pass
                else:
                    pass
        # IK: end
    vlg.close()
    return


def build_tree():
    global node_list
    global i_node_list
    global o_node_list
    
    # Initialize
    for node in node_list:
        node.parent_A = None
        node.parent_B = None
        node.children = []
    i_node_list = []
    o_node_list = []

    # Build tree
    for node in node_list:
        node_type = node.node_type
        name_A = node.name_A
        name_B = node.name_B
        name_Q = node.name_Q

        for node_it in node_list:
            # Find children 
            if (name_Q is not None) and \
               (node_it.name_A == name_Q or node_it.name_B == name_Q):
                node.children.append(node_it)
            # Find parent_A
            if (node_it.name_Q is not None) and \
               (node_it.name_Q == name_A):
                node.parent_A = node_it
            # Find parent_B
            if (node_it.name_Q is not None) and \
               (node_it.name_Q == name_B):
                node.parent_B = node_it

        if node_type == "input":
            i_node_list.append(node)

        if node_type == "output":
            o_node_list.append(node)

    return



def dfs_full():
    global i_node_list
    
    init_visit()

    stack = []
    pending = []
    assumed = []

    for i_node in i_node_list:
        stack.append(i_node)

    while len(stack) > 0:
        '''
        print("stack_list")
        for node_it in stack:
            print(node_it.node_name)
        print("pending list")
        for node_it in pending:
            print(node_it.node_name)
        print("assumed list")
        for node_it in assumed:
            print(node_it.node_name)
        print()
        '''
        node = stack.pop()
        #node.print()

        if not node.visit: 
            for child in node.children:
                if node.name_Q == child.name_A:
                    child.visit_A = True
                if node.name_Q == child.name_B:
                    child.visit_B = True

                if (child.name_A is None or child.visit_A) and \
                        (child.name_B is None or child.visit_B):
                    if child in pending:
                        pending.remove(child)
                    if child in assumed:
                        assumed.remove(child)
                    stack.append(child)
                else:
                    pending.append(child)
            node.visit = True

        while (len(stack) == 0) and len(pending) > 0:
            node = pending[0]
            pending.remove(node)

            if node.name_A is not None and not node.visit_A:
                if node.parent_A is not None:
                    stack.append(node)
                    if node in assumed:
                        assumed.remove(node)
                    if not node.parent_A in assumed:
                        assumed.append(node.parent_A)
            if node.name_B is not None and not node.visit_B:
                if node.parent_B is not None:
                    stack.append(node)
                    if node in assumed:
                        assumed.remove(node)
                    if not node.parent_B in assumed:
                        assumed.append(node.parent_B)
    
    if len(assumed) > 0:
        for node in assumed:
            for child in node.children:

                if child.parent_A and child.parent_A.node_name == node.node_name:
                    child.parent_A = None
                if child.parent_B and child.parent_B.node_name == node.node_name:
                    child.parent_B = None
            node.children = []
        dfs_full()
    '''
    for node in node_list:
        if node.node_name == '_28_':
            node.print()
    '''

    return
  

def find_all_path(src_name, dst_name):
    curr_path = []
    path_list = []
    init_visit()

    find_path_iter(src_name, dst_name, curr_path, path_list) 

    return path_list

def find_path_iter (src_name, dst_name, curr_path, path_list):
    global node_list
    for node in node_list:
        if node.node_name == src_name: 
            src_node = node

    src_node.visit = True
    curr_path.append(src_name)

    if src_name == dst_name:
        #print(curr_path)
        path_list.append(copy.deepcopy(curr_path))
    else:
        for child in src_node.children:
            if not child.visit:
                find_path_iter(child.node_name, dst_name, curr_path, path_list)
    curr_path.pop()
    src_node.visit = False
    return


def dom_analysis():
    global node_list
    
    node_name_list = []
    # Gen node_name list
    for node in node_list:
        node_name_list.append(node.node_name)
    # Init dom_list
    for node in node_list:
        node.dom_list = node_name_list[:]
     
    for node_i in node_list:
        #print("remove {}".format(node_i.node_name))
        # Remove node from the tree
        node_i.remove()
        # Run dfs
        dfs_full()
        # Renew dom_list
        for node_j in node_list:
            if node_j.node_type != "NDROT_RSFQ":
                if (node_j.name_A is not None and node_j.visit_A) or \
                        (node_j.name_B is not None and node_j.visit_B):
                    node_j.dom_list.remove(node_i.node_name)
            else:
                 #NDROT
                 if (node_j.name_A is not None and node_j.visit_A):
                     node_j.dom_list.remove(node_i.node_name)
            if node_i.node_name == "_116_0_":
                if node_j.node_name == "_004_2_":
                    print("dom_analysis: remove {}".format(node_i.node_name))
                    print(node_j.dom_list)

        '''
        print("when remove {}".format(node_i.node_name))
        for node in node_list:
            node.print()
        '''
        build_tree()

    for node in node_list:
        #print("Name: {} dom_list: {}".format(node.node_name, node.dom_list))
        pass

    return


def remove_backedge():
    global node_list

    dom_analysis()
    # Find backedge including all the trues and falses
    backedge_list = []
    false_list = []
    for node in node_list:
        if node.node_type == 'input' or node.node_type == 'output':
            continue
        for child in node.children:
            if child.node_name in node.dom_list:
                backedge_list.append((node.node_name, child.node_name))

    
    # Remove chain
    for s_edge in backedge_list:
        for e_edge in backedge_list:
            if s_edge[1] == e_edge[0]:
                #print(s_edge)
                #back_edge_list.remove(s_edge)
                false_list.append(s_edge)
                backedge_list = list(set(backedge_list) - set(false_list))

    
    # Remove low-depth-entry loop
    print(backedge_list)
    #'''
    real_backedge_list = []
    for edge_i in backedge_list: 
        edge_sameloop = []
        src, dst = edge_i
        path_list = find_all_path(dst, src)
        for edge_j in backedge_list:
            if (edge_i != edge_j):
                for path in path_list:
                    if edge_j[0] in path and edge_j[1] in path:
                        edge_sameloop.append(edge_j)

        #print("for {} edge_sameloop {}".format(edge_i, edge_sameloop))
        if len(edge_sameloop) > 0:
            edge_sameloop.append(edge_i)

            # Remove backedge
            real_backedge = None
            for backedge in edge_sameloop:
                for node in node_list:
                    if node.node_name == backedge[0]:
                        # FIXME: AD HOC approach
                        if node.node_type == "NDROT_RSFQ": 
                            real_backedge = backedge
                            

            '''
            for backedge in backedge_list:
                for node in node_list:
                    if node.node_name == backedge[0]:
                        for child in node.children:
                            if child.node_name == backedge[1]:
                                if node.name_Q == child.name_A:
                                    child.parent_A = None
                                if node.name_Q == child.name_B:
                                    child.parent_B = None
            # check depth 
            set_depth()
            real_backedge = None
            min_depth = math.inf 
            for backedge in edge_sameloop:
                for node in node_list:
                    if node.node_name == backedge[1]: 
                        curr_depth = max(node.depth_A, node.depth_B)
                        print("{} depth {}".format(node.node_name, curr_depth))
                if curr_depth < min_depth:
                    real_backedge = backedge
                    min_depth = curr_depth
            build_tree()
            '''
        else:
            real_backedge = edge_i
        if not real_backedge in real_backedge_list:
            real_backedge_list.append(real_backedge)
             
    #print("real:", real_backedge_list)
    #'''
    # Remove real backedge
    for backedge in real_backedge_list:
        for node in node_list:
            if node.node_name == backedge[0]:
                for child in node.children:
                    if child.node_name == backedge[1]:
                        if node.name_Q == child.name_A:
                            child.parent_A = None
                        if node.name_Q == child.name_B:
                            child.parent_B = None
                        node.children.remove(child)
    return real_backedge_list

def set_depth():
    global node_list, i_node_list
   
    '''
    print("here")
    for node in node_list:
        if node.parent_A is None and node.parent_B is None:
            node.print()
    '''

    # Initialize
    for node in node_list:
        node.depth_A = 0
        node.depth_B = 0
    
    # Set depth
    stack = []
    #for i_node in i_node_list:
    #    stack.append(i_node)
    for node in node_list:
        if node.parent_A is None and node.parent_B is None:
            if node.node_type != "input":
                #print("HERE")
                #node.print()
                node.depth_A = 1
                node.depth_B = 1
            stack.append(node)

    while len(stack) > 0:
        node = stack.pop()
        
        #print("stack_list")
        #for node_it in stack:
        #    print(node_it.node_name)
        
        #node.print()
        for child in node.children:
            #print("before child")
            #child.print()
            next_depth = max(node.depth_A, node.depth_B) + 1
            if node.name_Q == child.name_A and child.depth_A < next_depth:
                child.depth_A = next_depth
                stack.append(child)
            if node.name_Q == child.name_B and child.depth_B < next_depth:
                child.depth_B = next_depth
                stack.append(child)
            #print("after child")
            #child.print()
    return

def insert_dff():
    global o_node_list
    global node_list

    init_visit()

    stack = []
    net_id = 0
    node_id = 0

    max_depth_o = 0
    for o_node in o_node_list:
        max_depth_o = max(o_node.depth_A, max_depth_o)
    for o_node in o_node_list:
        o_node.depth_B = max_depth_o
        stack.append(o_node)


    while len(stack) > 0:
        node = stack.pop()
        
        if node.visit:
            continue
        node.visit = True
        if node.parent_A:
            stack.append(node.parent_A)
        if node.parent_B: 
            stack.append(node.parent_B)

        if (node.node_type == 'output' and node.parent_A is not None) or\
           (node.parent_A is not None and node.parent_B is not None):
            # check the depth balance
            depth_gap = node.depth_A - node.depth_B
            if depth_gap == 0:
                continue
            if depth_gap > 0:
                parent = node.parent_B
            if depth_gap < 0:
                parent = node.parent_A
            #node.print()
            # Insert DFFs
            for i in range(0, abs(depth_gap)):
                curr_name = "_ND{}_".format(node_id)
                if i == 0:
                    curr_Q = "_NT{}_".format(net_id) 
                    net_id += 1
                    if depth_gap > 0:
                        node.name_B = curr_Q
                    if depth_gap < 0:
                        node.name_A = curr_Q
                else:
                    curr_Q = curr_A
                if i == abs(depth_gap)-1:
                    curr_A = parent.name_Q
                else: 
                    curr_A = "_NT{}_".format(net_id) 

                new_node = Node(node_type = 'DFFT_RSFQ',
                                node_name = curr_name,
                                name_A = curr_A, 
                                name_B = None,
                                name_Q = curr_Q
                                )
                node_list.append(new_node)
                net_id += 1
                node_id += 1

    return

def set_split():
    global node_list

    for node in node_list:
        num_children = len(node.children)
        if num_children > 1:
            node.depth_split = math.ceil(math.log2(num_children))
            node.num_split = pow(2, node.depth_split)-1
        else:
            node.depth_split = 0
            node.num_split = 0

    return 

def gen_connection(real_backedges):
    global node_list
    
    ret_dict = dict()
    ret_dict['Type'] = []
    ret_dict['Name'] = []
    ret_dict['Depth'] = []
    ret_dict['A_type'] = []
    ret_dict['A_name'] = []
    ret_dict['A_depth_split'] = []
    ret_dict['A_dist_loop'] = []
    ret_dict['B_type'] = []
    ret_dict['B_name'] = []
    ret_dict['B_depth_split'] = []
    ret_dict['B_dist_loop'] = []
    ret_df = pd.DataFrame(ret_dict)

    for node in node_list:
        if node.node_type == 'input':
            continue

        df_row = dict()
        df_row['Type'] = node.node_type
        df_row['Name'] = node.node_name
        if node.node_type == 'output':
            df_row['Type'] = df_row['Type'] + "_{}".format(node.node_name)
        df_row['Depth'] = max(node.depth_A, node.depth_B)
        if node.parent_A:
            df_row['A_type'] = node.parent_A.node_type
            if node.parent_A.node_type == 'input':
                df_row['A_type'] = df_row['A_type'] + "_{}".format(node.parent_A.node_name)
            df_row['A_name'] = node.parent_A.node_name
            df_row['A_depth_split'] = int(node.parent_A.depth_split)
            edge_A = (node.parent_A.node_name, node.node_name)
            if edge_A in real_backedges:
                df_row['A_dist_loop'] = max(node.parent_A.depth_A, node.parent_A.depth_B) - max(node.depth_A, node.depth_B)
            else:
                df_row['A_dist_loop'] = None
        else:
            df_row['A_type'] = None
            df_row['A_name'] = None
            df_row['A_depth_split'] = None
            df_row['A_dist_loop'] = None

        if node.parent_B:
            df_row['B_type'] = node.parent_B.node_type
            if node.parent_B.node_type == 'input':
                df_row['B_type'] = df_row['B_type'] + "_{}".format(node.parent_B.node_name)
            df_row['B_name'] = node.parent_B.node_name
            df_row['B_depth_split'] = int(node.parent_B.depth_split)
            edge_B = (node.parent_B.node_name, node.node_name)
            if edge_B in real_backedges:
                df_row['B_dist_loop'] = max(node.parent_B.depth_A, node.parent_B.depth_B) - max(node.depth_A, node.depth_B)
            else:
                df_row['B_dist_loop'] = None
        else:
            df_row['B_type'] = None
            df_row['B_name'] = None
            df_row['B_depth_split'] = None
            df_row['B_dist_loop'] = None
    
        ret_df = ret_df.append(df_row, ignore_index=True)

    #print(ret_df)

    return ret_df


def gen_breakdown():
    global node_list 
    ''' 
    # Calculate width and depth
    node_dict = dict()
    for node in node_list:
        if node.node_type == 'input' or node.node_type == 'output':
            continue
        node_depth = max(node.depth_A, node.depth_B)
        try:
            node_dict[node_depth].append(node)
        except:
            node_dict[node_depth] = []
            node_dict[node_depth].append(node)

    max_depth = 0
    max_width = 0
    for depth, n_list in node_dict.items():
        width = len(n_list)
        if max_depth < depth:
            max_depth = depth
        if max_width < width:
            max_width = width
    # Generate breakdown
    depth_split_tree = math.ceil(math.log2(max_width))
    num_split_per_tree = pow(2, depth_split_tree)-1
    num_split_per_level = 1 + num_split_per_tree
    num_split = num_split_per_level * max_depth
    '''

    ret_dict = dict()
    #ret_dict["SPLITT_RSFQ"] = num_split

    for node in node_list:
        try:
            ret_dict['SPLITT_RSFQ'] += node.num_split
        except:
            ret_dict['SPLITT_RSFQ'] = 0
            ret_dict['SPLITT_RSFQ'] += node.num_split

        if node.node_type == 'input' or node.node_type == 'output':
            continue
        try:
            ret_dict[node.node_type] += 1
        except:
            ret_dict[node.node_type] = 1
    ret_df = pd.DataFrame(ret_dict, index = [0])
    return ret_df
        

def main(argv):
    global node_list 

    vlg_path = FLAGS.vlg
    clib_path = FLAGS.clib
    if FLAGS.loop == "True":
        loop_analysis = True
    else:
        loop_analysis = False
    unit_csv_dir = FLAGS.outdir
    unit_name = FLAGS.un

    #print(type(loop_analysis))
    #print(loop_analysis)
    
    # 1. Generate node list and build initial tree
    print("#1. Generate node list and build initial tree")
    gen_node_list(vlg_path, clib_path)
    build_tree()
    #for node in node_list:
    #    node.print()

    # 2. DFF insertion
    print("#2. DFF insertion")
    ### Remove backedges (i.e., edge from a loop's tail to a loop's head)
    if loop_analysis:
        print("Remove backedges (i.e., edge from a loop's tail to a loop's head)")
        find_edges = remove_backedge()
        print(find_edges)
    else:
        pass
    ### Set depth_A and depth_B for each node
    print("set depth")
    set_depth()

    ### Insert DFFs to balance the depth_A and the depth_B
    print("inert dff")
    insert_dff()
    build_tree() # Re-build the tree including the added DFFs
    
    # 3. Splitter insertion (in fact, not the insertion but the calculation)
    print("#3. Splitter insertion")
    set_split()

    if loop_analysis:
        # 4. Find the final backedges and Re-calculate the depth
        print("#4. Find the final backedges and re-calculate the depth")
        real_backedges = remove_backedge()
        set_depth()
        build_tree() # Re-build the tree to connect the backedges again
    else: 
        real_backedges = []
        set_depth()

    # 5. Generate the connection & breakdown dataframes (and Save them)
    print("#5. Generate the connection & breakdown dataframes (and Save them)")
    connection_df = gen_connection(real_backedges)
    #connection_df = gen_connection([])
    breakdown_df = gen_breakdown()
    if unit_name is None:
        unit_name = vlg_path.split('/')[-1].split('.')[0]
    else:
        pass
    connection_df = connection_df.sort_values (by=["Depth"])
    #display(connection_df)
    #print(breakdown_df)
    connection_df.to_csv("{}/{}_connection.csv".format(unit_csv_dir, unit_name), index=False)
    breakdown_df.to_csv("{}/{}_breakdown.csv".format(unit_csv_dir, unit_name), index=False)
    return

if __name__ == "__main__":
    app.run(main)
