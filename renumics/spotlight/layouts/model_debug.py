from renumics.spotlight import layout
from renumics.spotlight.layout import lenses, table, similaritymap, inspector, split, tab, metric, issues, confusion_matrix, histogram
from typing import Optional, List
from renumics.spotlight.analysis.typing import DataIssue
from renumics.spotlight import Audio, Image


def model_debug_classification(label: str='label', prediction: str='prediction', embedding: str=None, inspect: Optional[dict]=None, features: Optional[list]=None):
    

    # first column: table + issues 
    metrics = tab(metric(name="Accuracy", metric='accuracy', columns=[label, prediction]), weight=15)
    column1 = split([ metrics, tab(table(), weight=65)], weight=80, orientation="horizontal")
    column1 = split([ column1, tab(issues(), weight=40)], weight=80, orientation="horizontal")
    

    column2 = tab(confusion_matrix(name='Confusion matrix',x_column=label, y_column=prediction), weight=40)
    
    # third column: confusion matric, feature histograms (optional), embedding (optional)
    if features is not None:    
        histogram_list = []
        for idx, feature in enumerate(features):
            if idx >2:
                break
            h = histogram(name="Histogram {}".format(feature), column=feature, stack_by_column=label)
            histogram_list.append(h)

        row2 = tab(*histogram_list,  weight=40)
        column2 = split([column2, row2], weight=80, orientation='horizontal')

    
    if embedding is not None:       

        row3 = tab(similaritymap(name='Embedding', columns=[embedding], color_by_column=label), weight=40)

        column2 = split([column2, row3], orientation="horizontal")

    
  
    # fourth column: inspector    
    inspector_fields = []
    if inspect:
        for item, _type in inspect.items():
            if _type == Audio:
                inspector_fields.append(lenses.audio(item))
            elif _type == Image:
                inspector_fields.append(lenses.image(item))
            else:
                print('Type {} not supported by this layout.'.format(_type))

        inspector_fields.append(lenses.scalar(label))
        inspector_fields.append(lenses.scalar(prediction))

        inspector_view=inspector("Inspector", lenses=inspector_fields, num_columns=4)

    else:
        inspector_view = inspector("Inspector", num_columns=4)


    #build everything together
    column2.weight=40
    half1 = split([column1, column2], weight=80, orientation="vertical")
    half2 = tab(inspector_view, weight=40)


    nodes = [
        half1, half2
    ]

    the_layout = layout.layout(nodes)

    
    return the_layout
