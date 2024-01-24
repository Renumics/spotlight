import { Widget } from '../types';
import WidgetContainer from '../../components/ui/WidgetContainer';
import WidgetMenu from '../../components/ui/WidgetMenu';
import WidgetContent from '../../components/ui/WidgetContent';
import BrainIcon from '../../icons/Brain';
import DeleteIcon from '../../icons/Delete';
import tw from 'twin.macro';
import { KeyboardEvent, useCallback, useRef, useState } from 'react';
import Spinner from '../../components/ui/Spinner';
import Button from '../../components/ui/Button';
import chatService from '../../services/chat';
import { Problem } from '../../types';

interface Message {
    content: string;
    processing?: boolean;
    isError?: boolean;
}

const LLMWidget: Widget = () => {
    const [chat, setChat] = useState<Array<Message>>([]);
    const [processing, setProcessing] = useState(false);

    const queryInputRef = useRef<HTMLInputElement>(null);

    const handleKeyUp = useCallback((e: KeyboardEvent) => {
        if (!queryInputRef.current) return;

        if (e.key == 'Enter') {
            const query = queryInputRef.current.value;
            queryInputRef.current.value = '';
            setProcessing(true);
            setChat((state) => [...state, { content: query }]);

            const processQuery = async () => {
                try {
                    setChat((messages) => [
                        ...messages,
                        { content: '', processing: true },
                    ]);

                    const stream = chatService.stream(query);
                    for await (const response of stream) {
                        setChat((messages) => {
                            const lastMsg = messages[messages.length - 1];
                            return [
                                ...messages.slice(0, messages.length - 1),
                                {
                                    content: lastMsg.content + response,
                                    processing: true,
                                },
                            ];
                        });
                    }
                    setChat((messages) => {
                        const lastMsg = messages[messages.length - 1];
                        return [
                            ...messages.slice(0, messages.length - 1),
                            { content: lastMsg.content, processing: false },
                        ];
                    });
                } catch (e) {
                    const problem = e as Problem;
                    setChat((messages) => {
                        return [
                            ...messages.slice(0, messages.length - 1),
                            {
                                content: `${problem.title}\n${problem.detail}`,
                                processing: false,
                                isError: true,
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

    // TODO: scroll with new messages
    // TODO: only scroll message container

    return (
        <WidgetContainer>
            <WidgetMenu tw="flex flex-row justify-end">
                <Button onClick={clearChat}>
                    <DeleteIcon />
                </Button>
            </WidgetMenu>
            <WidgetContent tw="flex flex-col bg-gray-300 text-sm">
                <div tw="flex-grow flex flex-col p-1 space-y-1">
                    {chat.map((message, i) => (
                        <div
                            tw="bg-gray-100 px-1 py-0.5 rounded whitespace-pre-wrap"
                            css={[message.isError && tw`bg-red-100`]}
                            key={i}
                        >
                            {message.content}
                            {message.processing && <Spinner tw="w-4 h-4" />}
                        </div>
                    ))}
                </div>
                <div tw="p-1 relative">
                    <input
                        ref={queryInputRef}
                        disabled={processing}
                        tw="w-full bg-gray-100 disabled:bg-gray-200 py-0.5 px-1 border rounded"
                        placeholder={processing ? '' : 'Query'}
                        onKeyUp={handleKeyUp}
                    />
                    <div
                        tw="absolute top-0 left-0 h-full flex items-center"
                        css={[!processing && tw`hidden`]}
                    >
                        <Spinner tw="mx-1.5 w-4 h-4" />
                    </div>
                </div>
            </WidgetContent>
        </WidgetContainer>
    );
};

LLMWidget.key = 'LLMWidget';
LLMWidget.defaultName = 'Chat';
LLMWidget.icon = BrainIcon;

export default LLMWidget;
