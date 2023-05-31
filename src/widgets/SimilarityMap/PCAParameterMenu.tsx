import Menu from '../../components/ui/Menu';
import Select from '../../components/ui/Select';
import { PCANormalization, pcaNormalizations } from '../../services/data';

interface Props {
    pcaNormalization: PCANormalization;
    onChangePcaNormalization: (value?: PCANormalization) => void;
}

export const PCAParameterMenu = ({
    pcaNormalization,
    onChangePcaNormalization,
}: Props): JSX.Element => {
    return (
        <>
            <Menu.Title>PCA Settings</Menu.Title>
            <Menu.Subtitle>Normalization</Menu.Subtitle>
            <Menu.Item>
                <Select
                    value={pcaNormalization}
                    onChange={onChangePcaNormalization}
                    options={pcaNormalizations}
                />
            </Menu.Item>
        </>
    );
};
