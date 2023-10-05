"""Tree block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
from jinja2 import Environment, PackageLoader

try:
    from .. utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file, vec2flare_v2, is_circular
except:
    from utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file, vec2flare_v2, is_circular


# %% Set configuration properties
def set_config(config={}, margin={}, font={}, border={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    # Store configurations
    config['chart'] ='tree'
    config['title'] = kwargs.get('title', 'Tree - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'tree.html'), logger)
    config['figsize'] = kwargs.get('figsize', [1000, 600])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['cmap'] = kwargs.get('cmap', 'Set1')
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['margin'] = {**{"top": 40, "right": 10, "bottom": 10, "left": 10}, **margin}
    config['font'] = {**{'size': 10}, **font}
    config['notebook'] = kwargs.get('notebook', False)
    config['hierarchy'] = kwargs.get('hierarchy', [1, 2, 3, 4, 5])
    # return
    return config


# %% Set Edge properties
def set_edge_properties(df, **kwargs):
    """Set the edge properties.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data containing the following columns:
        'source'
        'target'
        'weight'
    logger : Object, (default: None)
        Logger.

    Returns
    -------
    df : pd.DataFrame()
        DataFrame.

    """
    # node_properties = kwargs.get('node_properties')
    logger = kwargs.get('logger', None)
    df = df.copy()
    df = pre_processing(df, labels=df.columns.values[:-1].astype(str))
    # Create unique dataframe, udpate weights
    # df = create_unique_dataframe(df, logger=logger)
    return df


def set_node_properties(df, **kwargs):
    """Set the node properties.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data containing the following columns:
        'source'
        'target'

    Returns
    -------
    dict_labels : dictionary()
        Dictionary containing the label properties.

    """
    # Get unique label
    col_labels = kwargs.get('labels', ['source', 'target'])
    logger = kwargs.get('logger', None)
    uilabels = set_labels(df, col_labels=col_labels, logger=logger)

    dict_labels = {}
    for i, label in enumerate(uilabels):
        dict_labels[label] = {'id': i,
                              'label': label,
                              'color': '#D33F6A',
                              'size': 10,
                              'tooltip': label,
                              'edge_size': 1,
                              'edge_color': '#000000',
                              'opacity': 0.95}

    # Return
    return dict_labels


def show(df, **kwargs):
    """Build and show the graph.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
    config : dict
        Dictionary containing configuration keys.
    node_properties : dict
        Dictionary containing the node properties.
        The node_properties are derived using the function: node_properties = d3.set_node_properties()

    Returns
    -------
    config : dict
        Dictionary containing updated configuration keys.

    """
    df = df.copy()
    node_properties = kwargs.get('node_properties')
    logger = kwargs.get('logger', None)
    config = update_config(kwargs, logger)
    config = config.copy()

    # Convert dict/frame.
    node_properties = convert_dataframe_dict(node_properties, frame=False)
    df = convert_dataframe_dict(df.copy(), frame=True)

    # Transform dataframe into input form for d3
    df.reset_index(inplace=True, drop=True)

    # Check whether dataframe is circular
    if is_circular(df, logger):
        logger.warning("The dataframe seems to be circular which can not be handled by this chart!")

    # Create the data from the input of javascript
    X = vec2flare_v2(df, node_properties, logger=logger)
    # Make it a string because the javascript is sensetive to quote differences.
    X = str(X)
    X = X.replace("'", '"')

    # Write to HTML
    return write_html(X, config, logger)


def write_html(X, config, logger=None):
    """Write html.

    Parameters
    ----------
    X : list of str
        Input data for javascript.
    config : dict
        Dictionary containing configuration keys.

    Returns
    -------
    None.

    """
    # Set width and height to screen resolution if None.
    width = 'window.screen.width' if config['figsize'][0] is None else config['figsize'][0]
    height = 'window.screen.height' if config['figsize'][1] is None else config['figsize'][1]

    content = {
        'json_data': X,
        'TITLE': config['title'],
        'WIDTH': width,
        'HEIGHT': height,
        'fontsize': config['font']['size'],
        'marginTop': config['margin']['top'],
        'marginRight': config['margin']['right'],
        'marginBottom': config['margin']['bottom'],
        'marginLeft': config['margin']['left'],
        'hierarchy': config['hierarchy'],
        'SUPPORT': config['support'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.tree', package_path='d3js'))

    index_template = jinja_env.get_template('tree.html.j2')

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html

