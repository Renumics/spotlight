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
    role: string;
    processing?: boolean;
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
            setChat((state) => [...state, { role: 'user', content: query }]);

            const processQuery = async () => {
                try {
                    setChat((messages) => [
                        ...messages,
                        { role: 'assistant', content: '', processing: true },
                    ]);

                    const stream = chatService.stream(query);
                    for await (const response of stream) {
                        setChat((messages) => {
                            const lastMsg = messages[messages.length - 1];
                            return [
                                ...messages.slice(0, messages.length - 1),
                                {
                                    role: 'assistant',
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
                            {
                                role: 'assistant',
                                content: lastMsg.content,
                                processing: false,
                            },
                        ];
                    });
                } catch (e) {
                    const problem = e as Problem;
                    setChat((messages) => {
                        return [
                            ...messages.slice(0, messages.length - 1),
                            {
                                role: 'error',
                                content: `${problem.title}\n${problem.detail}`,
                                processing: false,
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
            <WidgetContent tw="flex flex-col bg-gray-300 text-sm overflow-hidden">
                <div tw="flex-grow flex-shrink flex flex-col-reverse overflow-y-scroll">
                    <div tw="flex flex-col p-1 space-y-1">
                        {chat.map((message, i) => (
                            <div
                                tw="bg-gray-100 px-1 py-0.5 rounded whitespace-pre-wrap"
                                css={[
                                    message.role === 'error' && tw`bg-red-100`,
                                    message.role === 'user' && tw`bg-green-100 ml-4`,
                                    message.role !== 'user' && tw`mr-4`,
                                ]}
                                key={i}
                            >
                                <div tw="text-xxs uppercase font-bold text-midnight-600/30">
                                    {message.role}
                                </div>
                                <div>{message.content}</div>
                                <div tw="h-2 flex flex-row justify-end">
                                    {message.processing && <Spinner tw="w-2 h-2" />}
                                </div>
                            </div>
                        ))}
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
