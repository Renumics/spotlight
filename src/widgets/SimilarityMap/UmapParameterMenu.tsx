import LabeledSlider from '../../components/ui/LabeledSlider';
import Menu from '../../components/ui/Menu';
import Select from '../../components/ui/Select';
import Slider from '../../components/ui/Slider';
import Tooltip from '../../components/ui/Tooltip';
import { useEffect } from 'react';
import { UmapMetric, umapMetricNames } from '../../services/data';
import useWidgetConfig from '../useWidgetConfig';

const localGlobalMarks: { [key: number]: string } = {
    0: 'local',
    0.5: 'balanced',
    1: 'global',
};
const LocalGlobalTooltip = (key: number) => localGlobalMarks[key];

interface Props {
    umapNNeighbors: number;
    umapMetric: UmapMetric;
    umapMinDist: number;
    onChangeUmapNNeighbors: (value: number) => void;
    onChangeUmapMetric: (value?: UmapMetric) => void;
    onChangeUmapMinDist: (value: number) => void;
}

export const UmapSimpleMenu = ({
    onChangeUmapNNeighbors,
    onChangeUmapMinDist,
}: Props): JSX.Element => {
    const [localGlobalBalance, setLocalGlobalBalance] = useWidgetConfig(
        'umapMenuLocalGlobalBalance',
        0.5
    );

    useEffect(() => {
        if (localGlobalBalance < 0.5) {
            const alpha = 2 * localGlobalBalance;
            onChangeUmapNNeighbors(Math.round((1 - alpha) * 5 + alpha * 20));
            onChangeUmapMinDist((1 - alpha) * 0.01 + alpha * 0.15);
        } else {
            const alpha = 2 * (localGlobalBalance - 0.5);
            onChangeUmapNNeighbors(Math.round((1 - alpha) * 20 + alpha * 70));
            onChangeUmapMinDist((1 - alpha) * 0.15 + alpha * 0.5);
        }
    }, [localGlobalBalance, onChangeUmapNNeighbors, onChangeUmapMinDist]);

    return (
        <>
            <Menu.Subtitle>
                <Tooltip content="View local or global clusters within yout dataset.">
                    Clustering
                </Tooltip>
            </Menu.Subtitle>
            <Menu.Item>
                <Slider
                    tw="px-2"
                    value={localGlobalBalance}
                    marks={localGlobalMarks}
                    onRelease={setLocalGlobalBalance}
                    tooltip={LocalGlobalTooltip}
                    step={0.5}
                />
            </Menu.Item>
        </>
    );
};

export const UmapAdvancedMenu = ({
    umapNNeighbors,
    umapMinDist,
    onChangeUmapNNeighbors,
    onChangeUmapMinDist,
}: Props): JSX.Element => {
    return (
        <>
            <Menu.Subtitle>Neighbor Count</Menu.Subtitle>
            <Menu.Item>
                <LabeledSlider
                    tw="px-2"
                    min={2}
                    max={100}
                    step={1}
                    value={umapNNeighbors}
                    onRelease={onChangeUmapNNeighbors}
                    showTooltip={true}
                />
            </Menu.Item>
            <Menu.Subtitle>Min Distance</Menu.Subtitle>
            <Menu.Item>
                <LabeledSlider
                    tw="px-2"
                    min={0.01}
                    max={0.5}
                    step={0.01}
                    value={umapMinDist}
                    onRelease={onChangeUmapMinDist}
                    showTooltip={true}
                />
            </Menu.Item>
        </>
    );
};

export const UmapParameterMenu = (props: Props): JSX.Element => {
    const [isAdvanced, setIsAdvanced] = useWidgetConfig('umapMenuIsAdvanced', false);
    return (
        <>
            <Menu.Title>UMAP Settings</Menu.Title>
            <Menu.Switch value={isAdvanced} onChange={setIsAdvanced}>
                Show Advanced
            </Menu.Switch>
            {isAdvanced ? (
                <UmapAdvancedMenu {...props} />
            ) : (
                <UmapSimpleMenu {...props} />
            )}
            <Menu.Subtitle>Metric</Menu.Subtitle>
            <Menu.Item>
                <Select
                    value={props.umapMetric}
                    onChange={props.onChangeUmapMetric}
                    options={umapMetricNames}
                />
            </Menu.Item>
        </>
    );
};
