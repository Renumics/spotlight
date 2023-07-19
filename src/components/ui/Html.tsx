import tw, { styled } from 'twin.macro';

const StyledHtml = styled.div`
    ${tw`text-sm content-center items-center h-full w-full p-1 prose`}
`;

interface Props {
    html: string;
}

const Html = ({ html }: Props) => {
    return (
        <div tw="w-full h-full overflow-y-auto">
            <StyledHtml dangerouslySetInnerHTML={{ __html: html }} />
        </div>
    );
};

export default Html;
