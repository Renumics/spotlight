import { ReactNode, useCallback, useEffect, useState } from 'react';
import Dialog from './components/ui/Dialog';
import tw from 'twin.macro';
import Button from './components/ui/Button';
import styled, { keyframes } from 'styled-components';
import { X } from './icons';

const fadeIn = keyframes`
    0% {
        opacity: 0;
    }
    100% {
        opacity: 1;
    }
`;

const FadeInDiv = styled.div`
    animation: ${fadeIn} 0.35s ease-in-out;
`;

const StyledCTACard = styled.div`
    animation: ${fadeIn} 0.7s ease-in-out;
`;

const CTACard = ({
    className,
    href,
    background,
    children,
}: {
    className?: string;
    href: string;
    background: string;
    children: ReactNode;
}) => (
    <StyledCTACard
        className={'group' + (className ? ' ' + className : '')}
        tw="h-64 bg-white rounded shadow-md cursor-pointer relative overflow-hidden"
    >
        <div
            tw="w-full h-full absolute group-hover:opacity-90"
            style={{
                background,
            }}
        ></div>
        <div tw="relative w-full h-full">
            <a tw="h-full w-full p-4 block" href={href} target="_spotlight_cta">
                {children}
            </a>
        </div>
    </StyledCTACard>
);
const CTA_TIMEOUT_MS = 30 * 1000;

const CTADialog = () => {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const timeout = setTimeout(() => {
            setIsVisible(true);
        }, CTA_TIMEOUT_MS);

        return () => {
            clearTimeout(timeout);
        };
    }, []);

    const hide = useCallback(() => {
        setIsVisible(false);
    }, []);

    return (
        <Dialog isVisible={isVisible}>
            <FadeInDiv tw="w-[712px] relative mb-32">
                <Button tw="absolute right-2 top-2 w-6 h-6" onClick={hide}>
                    <X tw="w-full h-full" />
                </Button>
                <div tw="p-16 pb-2">
                    <h2 tw="text-center text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                        Thanks for giving Spotlight a spin!
                    </h2>
                    <p tw="mt-3 text-center text-xl text-gray-900">
                        How can we assist you in digging deeper into Spotlight and
                        speeding up your data-centric AI workflows?
                    </p>
                </div>
                <div tw="absolute w-full mt-6">
                    <div tw="grid grid-cols-3 space-x-4 px-4">
                        {[
                            <CTACard
                                background="linear-gradient(15deg, #9c56b8 0%, rgb(88 167 223) 100%)"
                                href=""
                                tw="bg-gray-400"
                                key="use-case"
                            >
                                <h3 tw="pt-2 text-xl tracking-wide font-extrabold text-white">
                                    Read background article
                                </h3>
                                <p tw="pt-2 text-base text-white">
                                    Step-by-step instructions for the use case.
                                </p>
                                <span tw="text-5xl float-right mt-8">📒</span>
                            </CTACard>,
                            <CTACard
                                background="linear-gradient(15deg, #183255 0%, rgb(88 167 223) 100%)"
                                href=""
                                tw="bg-gray-400"
                                key="own-data"
                            >
                                <h3 tw="pt-2 text-xl tracking-wide font-extrabold text-white">
                                    Apply to your use case
                                </h3>
                                <p tw="pt-2 text-base text-white">
                                    Load your own data in less than{' '}
                                    <b tw="font-bold">10 minutes</b>.
                                </p>
                                <span tw="text-5xl float-right mt-8">🚀</span>
                            </CTACard>,
                            <CTACard
                                href="https://renumics.com/docs/getting-started/?source=spotlight_cta#or-jump-right-into-using-spotlight-in-one-of-our-hosted-huggingface--spaces"
                                background="linear-gradient(15deg, rgba(126,63,251,1) 0%, rgba(252,70,107,1) 100%)"
                                tw="bg-gray-400"
                                key="huggingface"
                            >
                                <h3 tw="pt-2 text-xl tracking-wide font-extrabold text-white">
                                    Don’t know yet
                                </h3>
                                <p tw="pt-2 text-base text-white">
                                    Explore more interactive use cases hosted on{' '}
                                    <span tw="font-bold">huggingface</span>.
                                </p>
                                <span tw="text-5xl float-right mt-8">🤗</span>
                            </CTACard>,
                        ].sort((_a, _b) => 0.5 - Math.random())}
                    </div>
                </div>
            </FadeInDiv>
        </Dialog>
    );
};

export default CTADialog;
