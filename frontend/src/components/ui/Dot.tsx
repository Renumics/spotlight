import tw, { styled } from 'twin.macro';

export default styled.div.attrs(({ color }: { color: string | undefined }) => ({
    style: {
        backgroundColor: color,
    },
}))`
    ${tw`inline-block rounded-full p-1 ml-1 h-0 w-0`};
`;
