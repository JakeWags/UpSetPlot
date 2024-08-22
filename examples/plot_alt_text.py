"""
==========================================
Data Vis: Alt text generation in UpSetPlot
==========================================

Explore text description generation via upset-alttxt (2024).

When text description generation is enabled, there are no changes to the actual plot.
The generated text description can be accessed after creating the UpSet plot object.

"""

from matplotlib import pyplot as plt
from upsetplot import generate_counts
from upsetplot import UpSet

# Load the dataset into a DataFrame
example = generate_counts()

##########################################################################

print("Generating a plot AND grammar for textual description")
upset = UpSet(
    example,
    subset_size="count",
    sort_by="-cardinality",
    sort_categories_by="-cardinality",
    orientation="vertical",
    gen_grammar=True,
    meta_data={"items": "RANDOM ITEMS"},
)
upset.plot()
plt.suptitle("UpSet plot with text description generated'")
text_description = upset.get_alt_text()

print('==================================')
print('Long Description (markdown formatted)')
print('==================================')
print(text_description['longDescription'])

print('==================================')
print('Short Description')
print('==================================')
print(text_description['shortDescription'])

print('\n==================================')
print('Technique Description')
print('==================================')
print(text_description['techniqueDescription'])

plt.show()


print('\nNow to generate the same plot with no alt text generation')

# To disable grammar generation, simply ignore the gen_grammar parameter or set it to False.
upset = UpSet(
    example,
    subset_size="count",
    sort_by="-cardinality",
    sort_categories_by="-cardinality",
    orientation="vertical",
)

upset.plot()
plt.suptitle("UpSet plot with no alt text generation")

try:
    text_description = upset.get_alt_text()
except ValueError:
    print('gen_grammar must be set to True for any alt text generation.')

plt.show()
