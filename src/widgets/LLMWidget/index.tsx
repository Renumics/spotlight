import { Widget } from '../types';
import WidgetContainer from '../../components/ui/WidgetContainer';
import WidgetMenu from '../../components/ui/WidgetMenu';
import WidgetContent from '../../components/ui/WidgetContent';
import BrainIcon from '../../icons/Brain';
import DeleteIcon from '../../icons/Delete';
import tw from 'twin.macro';
import { KeyboardEvent, useRef, useState } from 'react';
import Spinner from '../../components/ui/Spinner';
import Button from '../../components/ui/Button';

const LLMWidget: Widget = () => {
    const [chat, setChat] = useState<Array<string>>([]);
    const [processing, setProcessing] = useState(false);

    const queryInputRef = useRef<HTMLInputElement>(null);

    const handleKeyUp = (e: KeyboardEvent) => {
        if (!queryInputRef.current) return;

        if (e.key == 'Enter') {
            const query = queryInputRef.current.value;
            queryInputRef.current.value = '';
            setProcessing(true);
            setChat((state) => [...state, query]);

            const processQuery = async () => {
                // TODO: replace sleep with call to backend
                await new Promise((r) => setTimeout(r, 2000));
                const response = 'LLM Response';
                setChat((state) => [...state, response]);
                setProcessing(false);
            };
            processQuery();
        }
    };

    const clearChat = () => setChat([]);

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
                        <div tw="bg-gray-100 px-1 py-0.5 rounded" key={i}>
                            {message}
                        </div>
                    ))}
                    {processing && (
                        <div tw="bg-gray-100 px-1 py-0.5 rounded">
                            <Spinner tw="w-4 h-4" />
                        </div>
                    )}
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
LLMWidget.defaultName = 'LLM';
LLMWidget.icon = BrainIcon;

export default LLMWidget;
