import tw from 'twin.macro';

import { Widget } from './types';
import WarningIcon from '../icons/Warning';
import { useDataset } from '../stores/dataset';
import Spinner from '../components/ui/Spinner';
import { DataIssue } from '../types';
import { MouseEvent, useState } from 'react';
import TriangleRight from '../icons/TriangleRight';
import TriangleDown from '../icons/TriangleDown';
import Markdown from '../components/ui/Markdown';
import CheckMark from '../icons/Check';
import Tooltip from '../components/ui/Tooltip';
import Info from '../components/ui/Info';

const icons = {
    low: tw(WarningIcon)`text-blue-600 h-5 w-5 mx-0.5`,
    medium: tw(WarningIcon)`text-yellow-600 h-5 w-5 mx-0.5`,
    high: tw(WarningIcon)`text-red-600 h-5 w-5 mx-0.5`,
};

const issueColors = {
    low: tw`bg-blue-100 border-b-blue-600 hover:bg-blue-200`,
    medium: tw`bg-yellow-100 border-b-yellow-600 hover:bg-yellow-200`,
    high: tw`bg-red-100 border-b-red-600 hover:bg-red-200`,
};

const iconColors = {
    low: tw`text-blue-600`,
    medium: tw`text-yellow-600`,
    high: tw`text-red-600`,
};

const elementColors = {
    low: tw`border-blue-600 hover:bg-blue-300`,
    medium: tw`border-yellow-600 hover:bg-yellow-300`,
    high: tw`border-red-600 hover:bg-red-300`,
};

interface IssueProps {
    issue: DataIssue;
}

const Issue = ({ issue }: IssueProps): JSX.Element => {
    const [collapsed, setCollapsed] = useState(true);

    const toggleCollapsed = () => setCollapsed((collapsed) => !collapsed);
    const selectRows = (event: MouseEvent<HTMLDivElement>) => {
        event.stopPropagation();
        useDataset.getState().selectRows(issue.rows);
    };
    const highlight = () => useDataset.getState().highlightRows(issue.rows);
    const dehighlight = () => useDataset.getState().dehighlightAll();

    const Icon = icons[issue.severity];

    return (
        <div
            css={[tw`flex flex-col border-b`, issueColors[issue.severity]]}
            onMouseOver={highlight}
            onFocus={highlight}
            onMouseLeave={dehighlight}
        >
            {
                // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/interactive-supports-focus
                <div
                    tw="flex flex-row px-1 h-7 text-sm items-center overflow-hidden align-middle"
                    onClick={toggleCollapsed}
                    role="button"
                >
                    <div css={[iconColors[issue.severity]]}>
                        {collapsed ? <TriangleRight /> : <TriangleDown />}
                    </div>
                    <Icon />
                    {
                        // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/interactive-supports-focus
                        <div
                            css={[
                                tw`rounded-full border border-yellow-600 text-xxs h-4 flex items-center justify-center whitespace-nowrap px-2 align-middle items-center align-middle mx-0.5`,
                                elementColors[issue.severity],
                            ]}
                            onClick={selectRows}
                            role="button"
                        >
                            {issue.rows.length}
                        </div>
                    }
                    <div
                        css={[
                            tw`flex-grow flex text-start items-center align-middle mx-1`,
                            !collapsed && tw`font-bold`,
                        ]}
                    >
                        {issue.title}
                    </div>
                    <div tw="flex">
                        {issue.columns?.map((column) => (
                            <div
                                key={column}
                                css={[
                                    tw`border rounded px-1 mx-0.5 text-xs`,
                                    elementColors[issue.severity],
                                ]}
                            >
                                {column}
                            </div>
                        ))}
                    </div>
                </div>
            }
            {collapsed || (
                <div tw="ml-6 text-xs">
                    <Markdown content={issue.description ?? ''} />
                </div>
            )}
        </div>
    );
};

const IssuesWidget: Widget = () => {
    const issues = useDataset((d) => d.issues);
    const rowsWithIssues = useDataset((d) => d.rowsWithIssues);
    const isAnalysisRunning = useDataset((d) => d.isAnalysisRunning);

    const highlight = () => useDataset.getState().highlightRows(rowsWithIssues ?? []);
    const dehighlight = useDataset.getState().dehighlightAll;
    const selectRows = () => useDataset.getState().selectRows(rowsWithIssues ?? []);

    return (
        <div tw="flex flex-col w-full h-full">
            <div tw="flex items-stretch bg-gray-100 h-6 border-b border-b-gray-400 divide-x divide-gray-400 text-xs overflow-hidden">
                {
                    // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/interactive-supports-focus
                    <div
                        tw="flex items-center px-1 hover:bg-gray-200"
                        onMouseOver={highlight}
                        onFocus={highlight}
                        onMouseLeave={dehighlight}
                        onClick={selectRows}
                        role="button"
                    >
                        {rowsWithIssues.length}{' '}
                        {rowsWithIssues.length == 1 ? 'row' : 'rows'} affected in total
                    </div>
                }
                <div tw="flex-grow"></div>
                <div tw="flex flex-row whitespace-nowrap items-center px-1 justify-end">
                    <div tw="w-full h-full p-0.5 flex items-center justify-center">
                        {isAnalysisRunning ? (
                            <Tooltip content="Running analysis">
                                <Spinner tw="w-4 h-4" />
                            </Tooltip>
                        ) : (
                            <Tooltip content="Analysis done">
                                <CheckMark />
                            </Tooltip>
                        )}
                    </div>
                </div>
            </div>
            <div tw="flex-grow flex flex-col overflow-auto">
                {issues.map((problem, i) => (
                    <Issue key={i} issue={problem} />
                ))}
                {!issues.length && isAnalysisRunning && <Info>Analysis running</Info>}
                {!issues.length && !isAnalysisRunning && <Info>No Issues found</Info>}
            </div>
        </div>
    );
};

IssuesWidget.key = 'IssuesWidget';
IssuesWidget.defaultName = 'Issues';
IssuesWidget.icon = WarningIcon;
export default IssuesWidget;
