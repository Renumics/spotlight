import tw from 'twin.macro';

export const Container = tw.div`
    flex flex-col items-stretch
    [height:60vh] [width:60vw]
    overflow-hidden
    text-sm
`;

export const Header = tw.div`
    p-1
    border-b border-gray-400
    text-xs font-bold
    flex flex-row
`;

export const Content = tw.div`
    flex flex-col flex-grow
    overflow-hidden
`;

export const Footer = tw.div`
    flex flex-row-reverse
    p-1
    border-t border-gray-400
`;
