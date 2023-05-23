import { FunctionComponent } from 'react';
import tw from 'twin.macro';
import Item from './Item';

const Divider = tw.hr`mb-1`;

const HorizontalDivider: FunctionComponent = () => (
    <Item>
        <Divider />
    </Item>
);
export default HorizontalDivider;
