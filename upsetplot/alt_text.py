def generate_grammar(
    df,
    intersections,
    totals,
    *,
    sort_by,
    sort_categories_by,
    min_degree=None,
    max_degree=None,
    include_empty_subsets=False,
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

    Returns
    -------
    The generated grammar compatible with UpSet 2 and Multinet's alt-text generator.
    """

    # default grammar state values required by UpSet 2/Multinet
    grammar = {
       "plotInformation": {
            "description": "",
            "sets": "",
            "items": ""
        },
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
            "hideNoSet": False
        },
        "visibleSets": [],
        "visibleAttributes": [],
        "bookmarkedIntersections": [],
        "collapsed": [],
        "plots": {
            "scatterplots": [],
            "histograms": [],
            "wordClouds": []
        },
        "allSets": [],
        # this value will likely be redundant with the latest alt-text generator release
        "altText": {
            "verbosity": "low",
            "explain": "full"
        },
        "rawData": {}, # this value may not be necessary
        "processedData": {},
        "accessibleProcessedData": {},
    }

    # TODO: update this when UpSet adds reverese sorting functionality
    if sort_by == "cardinality" or sort_by == "-cardinality":
        grammar["sortBy"] = "Size"
    if sort_by == "degree" or sort_by == "-degree":
        grammar["sortBy"] = "Degree"
    # this sort type is not supported by UpSet 2
    if sort_by == "input" or sort_by == "-input":
        grammar["sortBy"] = "Size"

    if sort_categories_by == "cardinality":
        grammar["sortVisibleBy"] = "Descending"
    if sort_categories_by == "-cardinality":
        grammar["sortVisibleBy"] = "Ascending"
    # this sort type is not supported by UpSet 2
    if sort_categories_by == "input" or sort_categories_by == "-input":
        grammar["sortVisibleBy"] = "Alphabetical"

    grammar["filters"]["hideEmpty"] = not include_empty_subsets
    grammar["filters"]["minVisible"] = (
        min_degree if min_degree is not None else 0
    )
    grammar["filters"]["maxVisible"] = (
        max_degree if max_degree is not None else 6
    )

    # these two values are the same as there is no way to "hide" sets
    grammar["visibleSets"] = totals.index.to_list()
    grammar["allSets"] = totals.index.to_list()

    return grammar


def get_alt_text():
    """
    Get the alt text for an UpSet plot.

    Returns:
        The alt text for the plot.
    """
    pass
