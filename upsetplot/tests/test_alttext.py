import pytest

from upsetplot import UpSet, fetch_alt_text, generate_counts, generate_grammar


@pytest.fixture
def sample_data():
    return generate_counts()


@pytest.fixture
def test_generate_grammar(sample_data):
    upset = UpSet(
        sample_data,
        subset_size="count",
        sort_by="-cardinality",
        sort_categories_by="-cardinality",
        orientation="vertical",
        gen_grammar=True,
    )

    grammar = upset.get_grammar()
    assert isinstance(grammar, dict)
    assert "version" in grammar

    return grammar


def test_generate_grammar_invalid_data():
    with pytest.raises(AttributeError):
        generate_grammar(
            df=None,
            intersections=None,
            totals=None,
            horizontal=False,
            sort_by="degree",
            sort_categories_by="cardinality",
            min_degree=None,
            max_degree=None,
            include_empty_subsets=False,
            include_data=False,
            meta_data=None,
        )


def test_generate_grammar_with_empty_subsets(sample_data):
    grammar = generate_grammar(
        df=sample_data,
        intersections=sample_data,
        totals=sample_data,
        horizontal=False,
        sort_by="degree",
        sort_categories_by="cardinality",
        min_degree=None,
        max_degree=None,
        include_empty_subsets=True,
        include_data=False,
        meta_data={"title": "Sample Plot", "caption": "This is a sample plot"},
    )
    assert grammar["filters"]["hideEmpty"] == False


def test_fetch_alt_text(test_generate_grammar):
    alt_text = fetch_alt_text(test_generate_grammar)
    assert isinstance(alt_text, dict)
    assert "techniqueDescription" in alt_text
    assert "shortDescription" in alt_text
    assert "longDescription" in alt_text


def test_fetch_alt_text_invalid_grammar():
    with pytest.raises(Exception, match="Failed to create alt text generator"):
        fetch_alt_text({})
