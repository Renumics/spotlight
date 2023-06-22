import tw from 'twin.macro';

import { Widget } from './types';
import WarningIcon from '../icons/Warning';
import { useDataset } from '../stores/dataset';
import LoadingIndicator from '../components/LoadingIndicator';
import { DatasetIssue } from '../types';

const icons = {
    warning: tw(WarningIcon)`text-yellow-600 h-5 w-5 mx-0.5`,
    error: tw(WarningIcon)`text-red-600 h-5 w-5 mx-0.5`,
};

interface IssueProps {
    problem: DatasetIssue;
}

const Issue = ({ problem }: IssueProps): JSX.Element => {
    const selectRows = () => useDataset.getState().selectRows(problem.rows);
    const highlight = () => useDataset.getState().highlightRows(problem.rows);
    const dehighlight = () => useDataset.getState().dehighlightAll();

    const Icon = icons[problem.severity];

    return (
        <button
            css={[
                tw`flex flex-row px-1 h-7 text-xs items-center border-b overflow-hidden align-middle`,
                problem.severity === 'warning' && tw`bg-yellow-100 border-b-yellow-600`,
                problem.severity === 'error' && tw`bg-red-100 border-b-red-600`,
            ]}
            onClick={selectRows}
            onMouseOver={highlight}
            onFocus={highlight}
            onMouseLeave={dehighlight}
        >
            <Icon />
            <div
                css={[
                    tw`rounded-full border border-yellow-600 text-xxs h-4 flex items-center justify-center whitespace-nowrap px-2 align-middle items-center align-middle mx-0.5`,
                    problem.severity === 'warning' && tw`border-yellow-600`,
                    problem.severity === 'error' && tw`border-red-600`,
                ]}
            >
                {problem.rows.length}
            </div>
            <div tw="flex-grow flex text-start items-center align-middle mx-1">
                {problem.description}
            </div>
        </button>
    );
};

const IssuesWidget: Widget = () => {
    const issues = useDataset((d) => d.issues);

    if (issues === undefined) {
        return <LoadingIndicator />;
    }

    return (
        <div tw="flex flex-col">
            {issues.map((problem, i) => (
                <Issue key={i} problem={problem} />
            ))}
        </div>
    );
};

IssuesWidget.key = 'IssuesWidget';
IssuesWidget.defaultName = 'Issues';
IssuesWidget.icon = WarningIcon;
export default IssuesWidget;
