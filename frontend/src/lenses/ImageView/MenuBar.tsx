import FitIcon from '../../icons/Reset';
import Button from '../../components/ui/Button';
import { FunctionComponent } from 'react';
import { BsArrowClockwise } from 'react-icons/bs';
import tw from 'twin.macro';

const Styles = tw.div`px-2 py-1 absolute top-0 right-0 items-start flex flex-row-reverse z-10`;

interface Props {
    onReset: () => void;
    onRotate: () => void;
}

const MenuBar: FunctionComponent<Props> = ({ onReset, onRotate }) => {
    return (
        <Styles>
            <Button tooltip={'Reset image'} onClick={onReset}>
                <FitIcon />
            </Button>
            <Button tooltip={'Rotate clockwise'} onClick={onRotate}>
                <BsArrowClockwise />
            </Button>
        </Styles>
    );
};

export default MenuBar;
