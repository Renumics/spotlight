import { useCallback, useEffect, useState } from 'react';
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

const CTACard = styled.div`
    animation: ${fadeIn} 0.7s ease-in-out;
`;

const CTA_TIMEOUT_MS = 30 * 1000;

const collections = [
    {
        name: 'Explore Locally',
        href: '#',
        imageSrc:
            'https://tailwindui.com/img/ecommerce-images/home-page-04-collection-01.jpg',
        description:
            'Curious about how our Spotlight performs offline? Delve into its features on your own computer.',
    },
    {
        name: 'Try it on your own Data',
        href: '#',
        imageSrc:
            'https://tailwindui.com/img/ecommerce-images/home-page-04-collection-02.jpg',
        description:
            'Integrate your data and uncover fascinating insights tailored just for you.',
    },
    {
        name: 'Explore more Spaces',
        href: '#',
        imageSrc:
            'https://tailwindui.com/img/ecommerce-images/home-page-04-collection-03.jpg',
        description:
            'Have a look at the various other examples we created ready to explore.',
    },
];

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
                        Continue your Journey with Spotlight
                    </h2>
                    <p tw="mt-3 text-center text-xl text-gray-900">
                        Dive deeper into the features and possibilities Spotlight has to
                        offer.
                    </p>
                </div>
                <div tw="absolute w-full mt-6">
                    <div tw="grid grid-cols-3 space-x-4 px-4">
                        {collections.map((collection) => (
                            <CTACard
                                key={collection.name}
                                className="group"
                                tw="h-64 bg-white rounded shadow-md cursor-pointer relative overflow-hidden"
                            >
                                <img
                                    src={collection.imageSrc}
                                    tw="object-cover w-full h-full absolute group-hover:opacity-75"
                                    alt={collection.name}
                                />
                                <div tw="w-full h-full relative group-hover:opacity-90">
                                    <a
                                        tw="h-full w-full"
                                        alt={collection.name}
                                        href={collection.href}
                                    >
                                        <h3 tw="px-4 pt-1 text-xl tracking-wide text-gray-900">
                                            {collection.name}
                                        </h3>
                                    </a>
                                </div>
                            </CTACard>
                        ))}
                    </div>
                </div>
            </FadeInDiv>
        </Dialog>
    );
};

export default CTADialog;
