import networkx as nx
import pickle
import networkx.algorithms.community as nx_comm
import networkx.algorithms.link_prediction as nx_lp
import random
import numpy as np
import matplotlib.pyplot as plt

def import_user_dict(filepath):
    """Import user info dictionary

    Parameters
    ----------
    filepath : str
        Filepath to user dictionary

    Returns
    -------
    user_dict : dict
        Dictionary of users and their followers
    """

    with open(filepath, 'rb') as p:
        user_dict = pickle.load(p)
    return user_dict

def edgelist_from_user_dict(user_dict):  
    """Create edgelist from user_dict
    
    Parameters
    ----------
    user_dict : dict
        Dictionary with users as keys and followers as values in the 'followers'
        subkey

    Returns
    -------
    edgelist : list of tuples
        Tuples (u, v) where u is the user and v is someone they follow
    """

    edgelist = []
    for user in user_dict.keys():
        for user_char in user_dict[user].keys():
            if user_char == 'followers':
                for follower in user_dict[user][user_char]:
                    edgelist.append((follower, user))
    return edgelist


def train_test_split_edgelist(edgelist, split_percent = .8):
    """Randomly samples the edgelist and splits into train and test data
    
    Parameters
    ----------
    edgelist : list of tuples
        Tuples (u, v) where u is the user and v is someone they follow
    
    split_percent : float
        Train-test split percentage. Default value: .8

    Returns
    -------
    train_data : list of tuples
        Portion of edgelist designated for training and predicting

    test_data : list of tuples
        Portion of edgelist set aside as holdout data for scoring predictions
    """

    random.shuffle(edgelist)
    train_data = edgelist[:int((len(edgelist)+1)*split_percent)]
    test_data = edgelist[int((len(edgelist)+1)*split_percent):]

    return train_data, test_data


def jaccard_coefficient(G, ebunch=None):
    """Randomly samples the edgelist and splits into train and test data. This
    is a copy of the 'jaccard_coefficient' function in NetworkX, which was not 
    set up for directed graphs when I started working on this.
    
    Parameters
    ----------
    G : A NetworkX graph

    ebunch : iterable of node pairs, optional (default = None)
        Jaccard coefficient will be computed for each pair of nodes
        given in the iterable. The pairs must be given as 2-tuples
        (u, v) where u and v are nodes in the graph. If ebunch is None
        then all non-existent edges in the graph will be used.
        Default value: None.


    Returns
    -------
    piter : iterator
        An iterator of 3-tuples in the form (u, v, p) where (u, v) is a
        pair of nodes and p is their Jaccard coefficient.
    
    Notes
    -----
    Wrap this function in a list() to assign an output to the function's output.
    """

    def predict(u, v):
        union_size = len(set(G[u]).union(set(G[v])))
        if union_size == 0:
            return 0
        shared = len(set(G[u]).intersection(set(G[v])))
        return shared / union_size

    return nx_lp._apply_prediction(G, predict, ebunch)


# Didn't end up using this because it gives all 1.0 and 0.0 coefficients
def community_jaccard_coefficients(G, community_lists):
    """Creates subgraphs of each detected community. This function doesn't work.
    I think it's because the subgraphs subdivide the graph so much that there 
    are very few following/follower nodes remaining. There might be other issues
    as well.
    """

    num_comms = len(community_lists)
    G_all_jcs = []
    for i in range(1,num_comms+1):
        cluster_comm = [n for n,v in G.nodes(data=True) if v['community'] == i]
        G_cluster = nx.subgraph(G, nbunch=cluster_comm)
        G_cluster_jc = jaccard_coefficient(G_cluster)
        G_all_jcs.append(list(G_cluster_jc))
    return G_all_jcs


def sort_jaccard_coefficients(coefficients_list, user='jack'):
    """Sort list of (u,v,p) tuples by p in descending order.

    Parameters
    ----------
    coefficients_list : list of tuples
        Unsorted list of (u,v,p) tuples
    
    user : str
        Username from the user_dict or graph nodes. Default is 'jack'

    Returns
    -------
    sorted_list : list of tuples
        Sorted list of (u,v,p) tuples
    """
    
    filtered_list = [tup for tup in coefficients_list if tup[0] == user]
    sorted_list = sorted(filtered_list, key= lambda x: x[2], reverse=True)
    return sorted_list


def get_top_n(sorted_list, G, n=10):
    """Select top n recommendations

    Parameters
    ----------
    sorted_list : list of tuples
        Sorted list of (u,v,p) tuples

    G : A NetworkX graph

    n : int
        Number of recommendations to provide

    Returns
    -------
    top_n_recs : list
        List of usernames to recommend to specific user
    """

    top_n_recs = []

    for row in sorted_list:
        if len(top_n_recs) < n:
            if G.has_edge(row[0], row[1]) == False:
                top_n_recs.append(row[1])
        else:
            return top_n_recs


def calc_correct_preds(top_n_recs, user, test_data):
    """Returns list of recommendations for user that were correctly predicted.

    Parameters
    ----------
    top_n_recs : list
        List of usernames to recommend to specific user
    
    user : str
        Username from the user_dict or graph nodes
    
    test_data : list of tuples
        Portion of edgelist set aside as holdout data for scoring predictions

    Returns
    -------
    correct_preds : list
        List of users that were correctly recommended to user

    Example
    -------
    If user 'jack' is recommended to follow users 'eric' and 'sylvia', and the
    test data shows that he actually does follow 'eric', then 'correct_preds'
    will be ['eric'].
    """
    
    correct_preds = []
    for item in top_n_recs:
        if (user, item) in test_data:
            correct_preds.append(item)
    return correct_preds


def calc_preds_precision(top_n_recs, user, test_data):
    """Calculates precision for recommendations

    Parameters
    ----------
    top_n_recs : list
        List of usernames to recommend to specific user
    
    user : str
        Username from the user_dict or graph nodes
    
    test_data : list of tuples
        Portion of edgelist set aside as holdout data for scoring predictions

    Returns
    -------
    precision : float
        Calculated as true positives / (true positives + false positives) from
        the top_n_recs compared to the test_data
    """
    
    correct_preds = calc_correct_preds(top_n_recs, user, test_data)
    total_correct = len(correct_preds)  # true positives
    total_preds = len(top_n_recs)  # true positives + false positives
    precision = total_correct/total_preds
    return precision


def get_random_node_sample(G, n=100, seed=123):
    """Return a random sample of nodes for evaluation

    Parameters
    ----------
    G : A NetworkX graph

    n : int
        Number of nodes to sample
    
    seed : int
        Random seed. Default value: 123

    Returns
    -------
    random_users : array-like
        List of users to be used in evaluation
    """

    random.seed(seed)
    random_users = random.sample(G.nodes, n)
    return random_users


def calculate_precision_at_k(G, jaccard_coefficients_list, test_data, n=100,
                             k=50, seed=123):
    """Calculates precision at k recommendations

    Parameters
    ----------
    G : A NetworkX graph

    jaccard_coefficients_list : list of tuples
        Unsorted list of (u,v,p) tuples
    
    test_data : list of tuples
        Portion of edgelist set aside as holdout data for scoring predictions

    n : int
        Number of nodes to sample. Default value: 100

    k : int
        Number of recommendations to provide. Default value: 50
    
    seed : int
        Random seed. Default value: 123

    Returns
    -------
    p_at_k_all : list of lists
        List of lists where each sublist corresponds to a user n and each
        element of the sublist represents precision at each level of k.
    """

    random_users = get_random_node_sample(G, n=n, seed=seed)

    p_at_k_all = []

    for user in random_users:
        p_at_k_user = []
        user_jcs_sorted = sort_jaccard_coefficients(jaccard_coefficients_list,
                                                    user=user)
        for k in range(1,k+1):
            user_top_n = get_top_n(user_jcs_sorted, G, n=k)
            precision = calc_preds_precision(user_top_n, user, test_data)
            p_at_k_user.append(precision)
        p_at_k_all.append(p_at_k_user)

    return p_at_k_all


def calculate_avg_precision_at_k(p_at_k_all):
    """Calculates average precision at k for all users at each level k

    Parameters
    ----------
    p_at_k_all : list of lists
        List of lists where each sublist corresponds to a user n and each
        element of the sublist represents precision at each level of k.
    
    Returns
    -------
    avg_p_at_k_all : list
        List where each element of sublists of p_at_k_all have been averaged
    
    Notes
    -----
    This function also produces a precision at k (p@k) chart
    """

    avg_p_at_k_all = np.mean(p_at_k_all, axis=0)

    x = [i for i in range(1,len(avg_p_at_k_all)+1)]
    y = avg_p_at_k_all

    fig, ax = plt.subplots(figsize=(6,4))
    plt.plot(x, y)
    plt.xlabel('k')
    plt.ylabel('Precision')
    plt.title(f'Precision at k for {len(p_at_k_all)} random users')
    plt.tight_layout()
    plt.show()
    
    return avg_p_at_k_all