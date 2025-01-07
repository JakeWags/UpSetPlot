from alttxt.enums import Level
from alttxt.generator import AltTxtGen
from alttxt.parser import Parser
from alttxt.tokenmap import TokenMap

"""
    alt_text.py
    -----------
    This file contains various conversions from the datatypes, structures,
    and values from UpSetPlot to Upset2 at upset.multinet.app.
    This is necessary to generate alt text with the Multinet API.
"""


def generate_grammar(
    df,
    intersections,
    totals,
    *,
    horizontal,
    sort_by,
    sort_categories_by,
    min_degree=None,
    max_degree=None,
    include_empty_subsets=False,
    include_data=False,
    meta_data=None,
):
    """
    Generate the grammar used by UpSet 2 and Multinet to generate alt text.

    Some values present in UpSet 2 will not be present in all implementations (e.g. Aggregation), so default values will be provided here

    .. versionadded:: 0.10

    Parameters
    ----------
    df : :class:`pandas.core.frame.DataFrame`
        The UpSet data DataFrame.
    intersections : :class:`pandas.core.series.Series`
        The list of intersections.
    totals : :class:`pandas.core.series.Series`
        The list of totals.
    horizontal: bool
        Plot orientation.
    sort_by : str
        The attribute to sort the sets by.
    sort_categories_by : str
        The attribute to sort the categories by.
    min_degree : number, optional
        The minimum degree (optional).
    max_degree : number, optional
        The maximum degree (optional).
    include_empty_subsets : bool, default=False
        Whether to include empty subsets (default: False).
    include_data : bool, default=False
        Whether to include subset data (default: False).

    Returns
    -------
    The generated grammar as a dictionary.
    """

    # default grammar state values required by UpSet 2/Multinet
    grammar = {
        "version": "0.1.0",  # alt-text grammar version
        "plotInformation": {
            "title": "",
            "caption": "",
            "description": "",
            "sets": "",
            "items": "",
        },
        "horizontal": False,
        "firstAggregateBy": "None",
        "firstOverlapDegree": 2,
        "secondAggregateBy": "None",
        "secondOverlapDegree": 2,
        "sortVisibleBy": "Alphabetical",
        "sortBy": "Size",
        "filters": {
            "maxVisible": 6,
            "minVisible": 0,
            "hideEmpty": True,
            "hideNoSet": False,
        },
        "visibleSets": [],
        "visibleAttributes": [],
        "bookmarks": [],
        "collapsed": [],
        "plots": {"scatterplots": [], "histograms": [], "wordClouds": []},
        "allSets": [],
    }

    grammar["horizontal"] = horizontal

    if meta_data is not None:
        grammar["plotInformation"]["title"] = meta_data.get("title", "")
        grammar["plotInformation"]["caption"] = meta_data.get("caption", "")
        grammar["plotInformation"]["description"] = meta_data.get("description", "")
        grammar["plotInformation"]["sets"] = meta_data.get("sets", "")
        grammar["plotInformation"]["items"] = meta_data.get("items", "")

    if sort_by == "degree":
        grammar["sortBy"] = "Degree"
        grammar["sortByOrder"] = "Descending"
    if sort_by == "-degree":
        grammar["sortBy"] = "Degree"
        grammar["sortByOrder"] = "Ascending"
    if sort_by == "cardinality":
        grammar["sortBy"] = "Size"
        grammar["sortByOrder"] = "Ascending"
    if sort_by == "-cardinality":
        grammar["sortBy"] = "Size"
        grammar["sortByOrder"] = "Descending"
    # this sort type is not supported by UpSet 2
    if sort_by == "input" or sort_by == "-input":
        grammar["sortBy"] = "Size"
        grammar["sortByOrder"] = "Descending"

    if sort_categories_by == "cardinality":
        grammar["sortVisibleBy"] = "Descending"
    if sort_categories_by == "-cardinality":
        grammar["sortVisibleBy"] = "Ascending"
    # this category sort type is not supported by UpSet 2
    if sort_categories_by == "input" or sort_categories_by == "-input":
        grammar["sortVisibleBy"] = "Alphabetical"

    grammar["filters"]["hideEmpty"] = not include_empty_subsets
    # if the min degree is above 0, the no set intersection should be hidden
    grammar["filters"]["hideNoSet"] = (
        min_degree > 0 if min_degree is not None else False
    )

    grammar["filters"]["minVisible"] = min_degree if min_degree is not None else 0
    grammar["filters"]["maxVisible"] = max_degree if max_degree is not None else 6

    grammar["visibleSets"] = totals.index.to_list()

    grammar["allSets"] = get_all_sets_info(totals)

    grammar["bookmarkedIntersections"] = [
        # generate intersection ids, or simply append index?
    ]

    if include_data:
        grammar["processedData"] = generate_processed_data(df, intersections, totals)
        grammar["rawData"] = {}
        grammar["accessibleProcessedData"] = generate_processed_data(
            df, intersections, totals, accessible=True
        )

    return grammar


def get_all_sets_info(totals):
    """
    Returns a list of objects, each containing the name and size of a set.

    Parameters:
    totals : dict
      A dictionary containing the set names as keys and their sizes as values.

    Returns:
    list: A list of dictionaries, where each dictionary represents a set and contains the keys "name" and "size".
          The "name" key holds the name of the set (str), and the "size" key holds the size of the set (int).
    """
    all_sets = []

    for set_name, set_size in totals.items():
        all_sets.append({"name": set_name, "size": set_size})

    return all_sets


def calculate_deviation(contained_sets, v_sets, sets, intersection_size, total_items):
    """
    Calculate the deviation of a given intersection.
    Based on deviation calculation in 2014 paper by Lex et al.

    Parameters:
    contained_sets : list
        The list of sets contained in the subset row (intersection)
    v_sets : list
        The list of all visible sets loaded into the UpSet plot
    sets : dict
        A dictionary containing the set names as keys and their sizes as values.
    intersection_size : int
        The size of the subset row (intersection)
    total_items : int
        The total number of items in the dataset

    Returns:
    float: The deviation of the intersection.
    """
    contained_product = 1
    for s in contained_sets:
        set_size = sets[s]
        contained_product *= set_size / total_items

    non_contained_product = 1
    for v in v_sets:
        if v not in contained_sets:
            set_size = sets[v]
            non_contained_product *= 1 - set_size / total_items

    dev = (intersection_size / total_items) - (
        contained_product * non_contained_product
    )

    return dev * 100


def get_set_membership_from_index(intersections, idx):
    """
    Returns a dictionary indicating the set membership of a given index.

    Parameters:
    intersections : :class:`pandas.core.series.Series`
        The list of intersections.
    idx : int
        The index to retrieve set membership for.

    Returns:
    dict: A dictionary where the keys are the set names and the values are either "Yes" or "No" indicating set membership.
    """
    names = intersections.index.names
    set_membership = {}
    for i, name in enumerate(names):
        set_membership[name] = "Yes" if intersections.index[idx][i] else "No"

    return set_membership


def get_degree_from_set_membership(set_membership):
    """
    Returns the degree of a given set membership.

    Parameters:
    set_membership : dict
        A dictionary indicating the set membership of a given index.

    Returns:
    int: The degree of the set membership.
    """
    return list(set_membership.values()).count("Yes")


def get_element_name_from_id(id):
    """
    Returns the element name (for use in alt-txt) from the given ID.
    (e.g) "Just cat1" or "cat1, cat2, and cat3"

    Parameters:
    id : str
        The ID to retrieve the element name for.
    """
    # remove "Subset_"
    # split the id by _ (this is the default delimiter between set names)
    # join with commas, but the last element should also have "and " prepended
    # if elements is only one element, return "Just {element}"
    stripped_id = id.replace("Subset~_~", "")
    elements = stripped_id.split("~_~")

    if len(elements) == 1:
        # the empty subset is named "Unincluded"
        #   and does not need "Just" prepended
        if elements[0] == "Unincluded":
            return "Unincluded"
        return f"Just {elements[0]}"

    element_name = ""
    for i, element in enumerate(elements):
        if i == len(elements) - 1:
            element_name += f"and {element}"
        else:
            element_name += f"{element}, "

    return element_name


def generate_intersection_id(intersections, idx):
    """
    Generates an intersection ID based on the given intersections and index.

    Parameters:
    intersections : :class:`pandas.core.series.Series`
        The list of intersections.
    idx : int
        The index to retrieve set membership for.

    Returns:
    str: The generated intersection ID.
    """
    names = intersections.index.names
    intersection_id = "Subset"
    set_membership = get_set_membership_from_index(intersections, idx)
    for name in names:
        # the delimiter "~_~" is used in UpSet2 in the internal ID
        intersection_id += f"~_~{name}" if set_membership[name] == "Yes" else ""

    # the empty subset is named "Subset_Unincluded" in UpSet2
    if intersection_id == "Subset":
        intersection_id += "~_~Unincluded"

    return intersection_id


def generate_processed_data(df, intersections, totals, accessible=False):
    processedData = {"values": {}, "order": []}
    # for every row in intersections:
    # generate the setMembership object
    for i in range(len(intersections)):
        id = generate_intersection_id(intersections, i)
        set_membership = get_set_membership_from_index(intersections, i)
        contained_sets = [
            name for name, membership in set_membership.items() if membership == "Yes"
        ]

        intersection_size = int(intersections.iat[i])

        deviation = calculate_deviation(
            contained_sets=contained_sets,
            v_sets=list(totals.index),
            sets=totals,
            intersection_size=intersection_size,
            total_items=totals.sum(),
        )

        processedData["values"][id] = {
            "id": id,
            "elementName": get_element_name_from_id(id),
            "setMembership": set_membership,
            "size": intersection_size,
            "type": "Subset",
            "degree": get_degree_from_set_membership(set_membership),
            "attributes": {},
            "deviation": deviation,
        }
        if accessible:
            processedData["values"][id]["deviation"] = deviation
        else:
            processedData["values"][id]["items"] = []
            processedData["order"].append(id)

    return processedData


def fetch_alt_text(grammar):
    """
    Get the alt text for an UpSet plot. Calls Multinet API

    Returns:
        The alt text for the plot.
    """
    try:
        parser = Parser(grammar)
        parsed_data = parser.get_data()
        parsed_grammar = parser.get_grammar()

        tokenmap: TokenMap = TokenMap(parsed_data, parsed_grammar, "title")

        gen = AltTxtGen(Level.DEFAULT, True, tokenmap, parsed_grammar)
    except Exception as e:
        raise Exception(f"Failed to create alt text generator: {e}")

    try:
        return gen.text
    except Exception as e:
        raise Exception(f"Failed to generate alt text: {e}")
