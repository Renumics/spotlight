import Lightbulb from '../../icons/Lightbulb';
import Tooltip from '../../components/ui/Tooltip';
import { formatNumber } from '../../dataformat';
import { FunctionComponent, useCallback } from 'react';
import { Dataset, useDataset } from '../../stores/dataset';
import { theme } from 'twin.macro';
import { DataColumn } from '../../types';

interface Props {
    column: DataColumn;
}

const RelevanceIndicator: FunctionComponent<Props> = ({ column }) => {
    const relevanceSelector = useCallback(
        (dataset: Dataset) => dataset.columnRelevance.get(column.key) ?? 0,
        [column]
    );
    const columnRelevance = useDataset(relevanceSelector);

    let relevanceColor = theme`colors.gray.300`;
    let relevanceMagnitude = 'No';
    if (columnRelevance > 0.8) {
        relevanceColor = theme`colors.red.600`;
        relevanceMagnitude = 'High';
    } else if (columnRelevance > 0.5) {
        relevanceColor = theme`colors.yellow.600`;
        relevanceMagnitude = 'Medium';
    } else if (columnRelevance > 0.2) {
        relevanceColor = theme`colors.gray.600`;
        relevanceMagnitude = 'Low';
    }

    const tooltipContent = `${relevanceMagnitude} Relevance (${formatNumber(
        columnRelevance ?? 0
    )})`;

    return (
        <Tooltip content={tooltipContent} disabled={!columnRelevance}>
            <Lightbulb
                tw="transition"
                style={{ color: relevanceColor, opacity: !columnRelevance ? 0 : 1 }}
            />
        </Tooltip>
    );
};

export default RelevanceIndicator;
