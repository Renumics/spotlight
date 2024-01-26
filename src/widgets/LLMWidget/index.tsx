import { Widget } from '../types';
import WidgetContainer from '../../components/ui/WidgetContainer';
import WidgetMenu from '../../components/ui/WidgetMenu';
import WidgetContent from '../../components/ui/WidgetContent';
import BrainIcon from '../../icons/Brain';
import DeleteIcon from '../../icons/Delete';
import FilterIcon from '../../icons/Filter';
import SelectionIcon from '../../icons/Selection';
import tw from 'twin.macro';
import { KeyboardEvent, useCallback, useRef, useState } from 'react';
import Spinner from '../../components/ui/Spinner';
import Button from '../../components/ui/Button';
import ToggleButton from '../../components/ui/ToggleButton';
import chatService, { type Message } from '../../services/chat';
import { Problem, SetFilter } from '../../types';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';
import Markdown from '../../components/ui/Markdown';
import { useDataset } from '../../stores/dataset';

interface RowsBadgeProps {
    rows: number[];
    name?: string;
}

const RowsBadge = ({ rows, name }: RowsBadgeProps): JSX.Element => {
    const select = () => useDataset.getState().selectRows(rows);
    const filter = () => useDataset.getState().addFilter(new SetFilter(rows, name));

    return (
        <div tw="flex flex-row">
            <div tw="flex-grow-0 flex-shrink-0 flex flex-row bg-gray-100 rounded divide-x divide-gray-400">
                <Button
                    tw="px-2 py-1 hover:bg-gray-200 flex flex-row font-normal"
                    onClick={select}
                >
                    <div tw="mr-1 font-bold flex justify-center items-center">
                        <SelectionIcon />
                    </div>
                    <div>{name}</div>
                </Button>
                <Button
                    tw="h-full px-2 py-1 hover:bg-gray-200 flex justify-center items-center"
                    onClick={filter}
                    tooltip="filter"
                >
                    <FilterIcon />
                </Button>
            </div>
            <div tw="flex-grow flex-shrink"></div>
        </div>
    );
};

const LLMWidget: Widget = () => {
    const [chat, setChat] = useState<Array<Message>>([]);
    const [processing, setProcessing] = useState(false);
    const [isContextVisible, setIsContextVisible] = useState(false);

    const queryInputRef = useRef<HTMLInputElement>(null);

    const handleKeyUp = useCallback((e: KeyboardEvent) => {
        if (!queryInputRef.current) return;

        if (e.key == 'Enter') {
            const query = queryInputRef.current.value;
            queryInputRef.current.value = '';
            setProcessing(true);
            setChat((state) => [
                ...state,
                { role: 'user', content: query, done: true },
            ]);

            const processQuery = async () => {
                try {
                    let content = '';

                    const stream = chatService.stream(query);
                    for await (const chunk of stream) {
                        content += chunk.content;
                        const message = { ...chunk, content };
                        if (message.done) {
                            content = '';
                        }
                        setChat((messages) => {
                            const lastMessage = messages[messages.length - 1];
                            if (lastMessage.done) {
                                return [...messages, message];
                            } else {
                                return [
                                    ...messages.slice(0, messages.length - 1),
                                    message,
                                ];
                            }
                        });
                    }
                } catch (e) {
                    const problem = e as Problem;
                    setChat((messages) => {
                        return [
                            ...messages,
                            {
                                role: 'error',
                                content: `${problem.title}\n${problem.detail}`,
                                done: true,
                            },
                        ];
                    });
                } finally {
                    setProcessing(false);
                }
            };
            processQuery();
        }
    }, []);

    const clearChat = () => setChat([]);

    return (
        <WidgetContainer>
            <WidgetMenu tw="flex flex-row justify-end">
                <ToggleButton
                    onChange={({ checked }) => setIsContextVisible(checked)}
                    tooltip="Show internal context"
                >
                    <BrainIcon />
                </ToggleButton>
                <Button tooltip="Clear Chat" onClick={clearChat} disabled={processing}>
                    <DeleteIcon />
                </Button>
            </WidgetMenu>
            <WidgetContent tw="flex flex-col bg-gray-300 text-sm overflow-hidden">
                <div tw="flex-grow flex-shrink flex flex-col-reverse overflow-y-scroll">
                    <div tw="flex flex-col">
                        <div tw="flex flex-col p-1 space-y-1">
                            {chat.map((message, i) => (
                                <div
                                    tw="px-1 py-0.5 rounded whitespace-pre-wrap"
                                    css={[
                                        message.role === 'assistant' && tw`bg-gray-100`,
                                        message.role === 'artifact' && tw`px-0 py-0`,
                                        message.role === 'error' && tw`bg-red-100`,
                                        message.role === 'context' &&
                                            tw`bg-gray-300 border border-dashed border-gray-600`,
                                        message.role === 'context' &&
                                            !isContextVisible &&
                                            tw`hidden`,
                                        message.role === 'user' &&
                                            tw`bg-green-100 ml-4`,
                                        message.role !== 'user' && tw`mr-4`,
                                    ]}
                                    key={i}
                                >
                                    <div tw="text-xxs uppercase font-bold text-midnight-600/30">
                                        {message.role != 'artifact' && message.role}
                                    </div>
                                    <div>
                                        {message.content_type === 'text/sql' && (
                                            <SyntaxHighlighter
                                                language="sql"
                                                style={dracula}
                                            >
                                                {message.content}
                                            </SyntaxHighlighter>
                                        )}
                                        {message.content_type === 'text/markdown' && (
                                            <Markdown content={message.content} />
                                        )}
                                        {message.content_type === 'rows' && (
                                            <RowsBadge
                                                rows={JSON.parse(message.content).rows}
                                                name={JSON.parse(message.content).name}
                                            />
                                        )}
                                        {(message.content_type === 'text/plain' ||
                                            message.content_type === undefined) &&
                                            message.content}
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div tw="h-2 overflow-hidden px-2">
                            {processing && <Spinner tw="w-2 h-2" />}
                        </div>
                    </div>
                </div>
                <div tw="flex-grow-0 flex-shrink-0 p-1 relative overflow-hidden">
                    <input
                        ref={queryInputRef}
                        disabled={processing}
                        tw="w-full bg-gray-100 disabled:bg-gray-200 py-0.5 px-1 border rounded"
                        placeholder={processing ? '' : 'Query'}
                        onKeyUp={handleKeyUp}
                    />
                </div>
            </WidgetContent>
        </WidgetContainer>
    );
};

LLMWidget.key = 'LLMWidget';
LLMWidget.defaultName = 'Chat';
LLMWidget.icon = BrainIcon;

export default LLMWidget;
