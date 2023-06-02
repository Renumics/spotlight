import tw, { styled } from 'twin.macro';

const StyledHtml = styled.div`
    ${tw`text-sm content-center items-center h-full w-full p-1 overflow-y-auto prose`}
`;

interface Props {
    html: string;
}

const Html = ({ html }: Props) => {
    return <StyledHtml dangerouslySetInnerHTML={{ __html: html }} />;
};

export default Html;
