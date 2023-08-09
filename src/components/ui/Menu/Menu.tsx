import tw, { styled } from 'twin.macro';
import ActionInput from './ActionInput';
import ColumnSelect from './ColumnSelect';
import HorizontalDivider from './HorizontalDivider';
import Input from './Input';
import Item from './Item';
import MultiColumnSelect from './MultiColumnSelect';
import Subtitle from './Subtitle';
import Switch from './Switch';
import Title from './Title';
import TextArea from './TextArea';

// Helper to attach properties to a function component
// https://stackoverflow.com/questions/54812930/how-to-add-properties-to-styled-component-with-typescript
function withProperties<A, B extends object>(component: A, properties: B): A & B {
    Object.keys(properties).forEach((key) => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (component as any)[key] = (properties as any)[key];
    });
    return component as A & B;
}

const Menu = styled.div`
    ${tw`flex flex-col text-sm`}

    label {
        ${tw`text-midnight-600 px-1`}
    }
`;

const Properties = {
    Item,
    Title,
    Subtitle,
    Switch,
    Input,
    ActionInput,
    MultiColumnSelect,
    ColumnSelect,
    HorizontalDivider,
    TextArea,
} as const;

const MenuWithProperties: typeof Menu & typeof Properties = withProperties(
    Menu,
    Properties
);
export default MenuWithProperties;
